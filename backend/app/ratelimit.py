"""A small in-memory rate limiter to protect the free LLM quota.

Sliding window: we remember the times of recent requests per client IP and
refuse new ones once there are too many in the window. There is also a global
daily cap for all users together.

In-memory is fine for one server. With several servers (or AWS Lambda) the
counters would live in a shared store such as DynamoDB or Redis instead.
"""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from .config import settings

_per_ip: dict[str, deque] = defaultdict(deque)
_global: deque = deque()


def client_ip(request: Request) -> str:
    # Render and other hosts put the real client IP first in X-Forwarded-For.
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _trim(q: deque, window: float, now: float) -> None:
    while q and now - q[0] > window:
        q.popleft()


def check_rate_limit(request: Request) -> None:
    now = time.time()
    ip_q = _per_ip[client_ip(request)]
    _trim(ip_q, 3600, now)
    _trim(_global, 86400, now)
    if len(_global) >= settings.daily_limit:
        raise HTTPException(429, "The demo hit its daily limit. Please try again tomorrow.")
    if len(ip_q) >= settings.hourly_limit_per_ip:
        raise HTTPException(429, "Too many requests. Please wait a bit and try again.")
    ip_q.append(now)
    _global.append(now)


def reset() -> None:
    _per_ip.clear()
    _global.clear()
