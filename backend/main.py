import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis

from backend.database import engine, Base
from backend.middleware.auth import AuthMiddleware, PlanTierRateLimitMiddleware

# Import routers
from backend.routers.auth import router as auth_router
from backend.routers.projects import router as projects_router
from backend.routers.jobs import router as jobs_router
from backend.routers.billing import router as billing_router
from backend.routers.api_keys import router as api_keys_router
from backend.routers.viewer import router as viewer_router
from backend.routers.assets import router as assets_router
from backend.routers.external_api import router as external_api_router

# Import Agent and Evolution Routers
from backend.agents.intent_parser.agent import router as intent_parser_router
from backend.agents.drawing_generator.agent import router as drawing_generator_router
from backend.agents.drawing_interpreter.agent import router as drawing_interpreter_router
from backend.agents.model_synthesizer.agent import router as model_synthesizer_router
from backend.agents.render_engine.agent import router as render_engine_router
from backend.agents.animation_director.agent import router as animation_director_router
from backend.agents.interactive_xr.agent import router as interactive_xr_router
from backend.agents.simulation.agent import router as simulation_router
from backend.agents.standards_validator.agent import router as standards_validator_router
from backend.agents.bom_estimator.agent import router as bom_estimator_router
from backend.evolution.router import router as evolution_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="ProtoForge AI Backend",
        description="The REST API Gateway and Agent Orchestrator for ProtoForge AI",
        version="0.1.0"
    )

    # CORS configuration - Allow Vercel origin and local testing origins
    origins = [
        "http://localhost:3000",
        "https://protoforge-frontend.vercel.app",  # Mock Vercel deployment
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
    app.add_middleware(PlanTierRateLimitMiddleware)
    app.add_middleware(AuthMiddleware)

    # Mount Routers
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(jobs_router)
    app.include_router(billing_router)
    app.include_router(api_keys_router)
    app.include_router(viewer_router)
    app.include_router(assets_router)
    app.include_router(external_api_router)

    # Mount Agent and Evolution Routers
    app.include_router(intent_parser_router, prefix="/api/v1")
    app.include_router(drawing_generator_router, prefix="/api/v1")
    app.include_router(drawing_interpreter_router, prefix="/api/v1")
    app.include_router(model_synthesizer_router, prefix="/api/v1")
    app.include_router(render_engine_router, prefix="/api/v1")
    app.include_router(animation_director_router, prefix="/api/v1")
    app.include_router(interactive_xr_router, prefix="/api/v1")
    app.include_router(simulation_router, prefix="/api/v1")
    app.include_router(standards_validator_router, prefix="/api/v1")
    app.include_router(bom_estimator_router, prefix="/api/v1")
    app.include_router(evolution_router, prefix="/api/v1")

    # Mount static assets folder for 3D model, render, and animation file serving
    from fastapi.staticfiles import StaticFiles
    assets_dir = "/home/team/shared/protoforge/backend/assets"
    os.makedirs(assets_dir, exist_ok=True)
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Health Endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "version": "0.1.0"
        }

    # Startup & Shutdown Events
    @app.on_event("startup")
    async def startup_event():
        # Create database tables if they do not exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        app.state.redis = aioredis.from_url(redis_url)

    @app.on_event("shutdown")
    async def shutdown_event():
        await engine.dispose()
        if hasattr(app.state, "redis"):
            await app.state.redis.close()

    return app

app = create_app()
