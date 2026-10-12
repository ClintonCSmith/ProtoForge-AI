"""API Key validation and plan-tier rate limiting middleware."""
import time
import os
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from uuid import UUID


# Rate limiting state
rate_limits: dict[str, list[float]] = defaultdict(list)

PLAN_LIMITS = {
    "free": {"requests_per_minute": 10, "projects_per_month": 1},
    "starter": {"requests_per_minute": 30, "projects_per_month": 10},
    "professional": {"requests_per_minute": 100, "projects_per_month": 50},
    "enterprise": {"requests_per_minute": 500, "projects_per_month": -1},
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting by API key or user plan tier."""
    
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key", "")
        plan = "free"
        
        if api_key and api_key.startswith("pf_"):
            # Look up plan from API key (simplified)
            plan = "professional"
        
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        client_id = api_key or request.client.host if request.client else "unknown"
        rate_limits[client_id] = [t for t in rate_limits[client_id] if t > minute_ago]
        
        if len(rate_limits[client_id]) >= limits["requests_per_minute"]:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Maximum {limits['requests_per_minute']} requests per minute for {plan} plan.",
                    "plan": plan,
                    "limit": limits["requests_per_minute"],
                    "retry_after_seconds": 60,
                }
            )
        
        rate_limits[client_id].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limits["requests_per_minute"])
        response.headers["X-RateLimit-Remaining"] = str(max(0, limits["requests_per_minute"] - len(rate_limits[client_id])))
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests with timing."""
    
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        print(f"[API] {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
        response.headers["X-Response-Time-Ms"] = str(int(duration * 1000))
        return response


async def validate_api_key(request: Request):
    """Dependency to validate X-API-Key header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "missing_api_key",
                "message": "X-API-Key header is required. Get your API key from the dashboard.",
                "docs": "/docs",
            }
        )
    # In production, validate against database
    if not api_key.startswith("pf_"):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "invalid_api_key",
                "message": "Invalid API key format. Keys should start with 'pf_'.",
            }
        )
    return api_key