import os
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "mock-supabase-secret-key-1234567890")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Exclude public and documentation routes
        if path in ["/health", "/docs", "/openapi.json", "/redoc"] or path.startswith("/auth/") or path.startswith("/view/"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            request.state.user = None
            if path.startswith("/projects") or path.startswith("/jobs") or path.startswith("/billing") or path.startswith("/api-keys"):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    content={"detail": "Missing or invalid authorization credentials."}
                )
            return await call_next(request)

        token = auth_header.split(" ")[1]
        try:
            # Decode the Supabase JWT
            payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
            request.state.user = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role")
            }
        except JWTError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"Invalid token: {str(e)}"}
            )

        return await call_next(request)


class PlanTierRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We can implement simple rate-limit checks for generating projects
        if request.url.path.endswith("/generate") and request.method == "POST":
            # For demonstration, we verify that user state is injected
            user = getattr(request.state, "user", None)
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required for generation."}
                )
        return await call_next(request)
