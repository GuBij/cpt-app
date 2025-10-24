import time

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, throttle_rate: int = 60):
        super().__init__(app)
        self._throttle_rate: int = throttle_rate
        self._request_log: dict[str, list[float]] = {}  # Track timestamps per IP

    async def dispatch(self, request: Request, call_next):
        client_ip: str = request.client.host
        now: float = time.time()

        # Clean up old request logs older than 60 seconds
        self._request_log = {
            ip: [ts for ts in times if ts > now - 60]
            for ip, times in self._request_log.items()
        }

        ip_history: list[float] = self._request_log.get(client_ip, [])

        if len(ip_history) >= self._throttle_rate:
            raise HTTPException(status_code=429, detail="Too many requests")

        ip_history.append(now)
        self._request_log[client_ip] = ip_history

        return await call_next(request)
