import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as aioredis

from backend.database import engine, Base
from backend.middleware.auth import RateLimitMiddleware, RequestLoggingMiddleware

# Import business routers only — agent sub-app stubs removed (all agents run as Celery tasks)
from backend.routers.auth import router as auth_router
from backend.routers.projects import router as projects_router
from backend.routers.jobs import router as jobs_router
from backend.routers.billing import router as billing_router
from backend.routers.api_keys import router as api_keys_router
from backend.routers.viewer import router as viewer_router
from backend.routers.assets import router as assets_router
from backend.routers.external_api import router as external_api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="ProtoForge AI Backend",
        description="The REST API Gateway and Agent Orchestrator for ProtoForge AI",
        version="0.1.0"
    )

    # CORS configuration
    origins = [
        "http://localhost:3000",
        "https://protoforge-frontend.vercel.app",
        "*"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount Middlewares
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Our team has been notified.",
                "request_id": request.headers.get("X-Request-ID", ""),
            },
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": f"The requested resource '{request.url.path}' was not found.",
                "path": request.url.path,
            },
        )

    # Mount business Routers only (all agent work is via Celery tasks + Orchestrator)
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(jobs_router)
    app.include_router(billing_router)
    app.include_router(api_keys_router)
    app.include_router(viewer_router)
    app.include_router(assets_router)
    app.include_router(external_api_router)

    # Mount static assets folder
    from fastapi.staticfiles import StaticFiles
    assets_dir = "/home/team/shared/protoforge/backend/assets"
    os.makedirs(assets_dir, exist_ok=True)
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Health Endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        db_status = getattr(app.state, "db_status", "unknown")
        redis_status = getattr(app.state, "redis_status", "unknown")
        overall = "healthy" if (db_status == "connected" and redis_status == "connected") else "degraded"
        return {
            "status": overall,
            "database": db_status,
            "redis": redis_status,
            "version": "0.1.0"
        }

    # Startup & Shutdown Events
    @app.on_event("startup")
    async def startup_event():
        app.state.db_status = "unavailable"
        app.state.redis_status = "unavailable"
        # Initialize schema / verify DB connectivity without crashing if the
        # database is not reachable (e.g. local dev with no Postgres running).
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            app.state.db_status = "connected"
        except Exception as e:  # noqa: BLE001
            print(f"[startup] WARNING: database unavailable ({type(e).__name__}: {e}); running degraded")
            app.state.db_status = "unavailable"
        # Redis client (lazy connect — does not block startup).
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        app.state.redis = aioredis.from_url(redis_url)
        try:
            await app.state.redis.ping()
            app.state.redis_status = "connected"
        except Exception as e:  # noqa: BLE001
            print(f"[startup] WARNING: redis unavailable ({type(e).__name__}: {e}); running degraded")
            app.state.redis_status = "unavailable"

    @app.on_event("shutdown")
    async def shutdown_event():
        await engine.dispose()
        if hasattr(app.state, "redis"):
            await app.state.redis.close()

    return app

app = create_app()