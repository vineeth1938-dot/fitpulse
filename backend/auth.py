"""Authentication (Supabase JWT) and per-user rate limiting. Both are per process, in memory."""
import base64
import json
import logging
import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException
from supabase_auth.errors import AuthError

import db

log = logging.getLogger("fitpulse.auth")

TOKEN_TTL_S = 60      # a revoked session can stay valid this long
CACHE_MAX = 1000
WINDOW_S = 60
LIMITS = {"std": 60, "ai": 10}  # requests per user per minute; "ai" buckets call paid models
# shortcut: in-memory counters reset on restart and are not shared between instances; use Redis if scaling out

_lock = threading.Lock()  # dependencies run in a thread pool, so the shared dicts need one
_token_cache: dict[str, tuple[str, float]] = {}
_hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)


def reset_state() -> None:
    with _lock:
        _token_cache.clear()
        _hits.clear()


def _looks_like_live_jwt(token: str) -> bool:
    """Cheap local pre-check so junk and expired tokens never cost a Supabase call. It does NOT verify the
    signature: Supabase does that in _lookup."""
    parts = token.split(".")
    if len(parts) != 3:
        return False
    try:
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        return isinstance(payload, dict) and float(payload["exp"]) > time.time()
    except (ValueError, KeyError, TypeError):
        return False


def _lookup(token: str) -> str | None:
    """Ask Supabase who this token belongs to. None means the token is invalid or expired."""
    try:
        res = db.client().auth.get_user(token)
    except AuthError:
        return None
    return res.user.id if res and res.user else None


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(401, detail, headers={"WWW-Authenticate": "Bearer"})


def current_user(authorization: str | None = Header(default=None)) -> str:
    scheme, _, token = (authorization or "").partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized("Sign in required")
    if not _looks_like_live_jwt(token):
        raise _unauthorized("Invalid or expired session")
    now = time.monotonic()
    with _lock:
        hit = _token_cache.get(token)
    if hit and hit[1] > now:
        return hit[0]
    user_id = _lookup(token)  # network call, outside the lock
    if user_id is None:
        raise _unauthorized("Invalid or expired session")
    with _lock:
        if len(_token_cache) >= CACHE_MAX:  # drop the entries closest to expiry first
            for key in sorted(_token_cache, key=lambda k: _token_cache[k][1])[: CACHE_MAX // 2]:
                _token_cache.pop(key, None)
        _token_cache[token] = (user_id, now + TOKEN_TTL_S)
    return user_id


def rate_limit(bucket: str):
    """Dependency factory: at most LIMITS[bucket] requests per user per WINDOW_S seconds."""
    def check(user: str = Depends(current_user)) -> None:
        now = time.monotonic()
        with _lock:
            hits = _hits[(user, bucket)]
            while hits and hits[0] <= now - WINDOW_S:
                hits.popleft()
            if len(hits) >= LIMITS[bucket]:
                retry = max(1, int(hits[0] + WINDOW_S - now) + 1)
                raise HTTPException(429, "Too many requests, please slow down", headers={"Retry-After": str(retry)})
            hits.append(now)
            if len(_hits) > 5000:  # drop idle users
                for key in [k for k, q in _hits.items() if not q or q[-1] <= now - WINDOW_S]:
                    _hits.pop(key, None)
    return check
