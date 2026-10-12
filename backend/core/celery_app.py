import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "protoforge_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "agents.intent_parser",
        "agents.drawing_generator",
        "agents.drawing_interpreter",
        "agents.model_synthesizer",
        "agents.render_engine",
        "agents.animation_director",
        "agents.interactive_xr",
        "agents.simulation",
        "agents.bom_estimator",
        "agents.standards_validator",
        "agents.self_evolution",
        "agents.orchestrator.agent",
    ]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat Schedule for Agent 12 (Self-Evolution Engine)
celery_app.conf.beat_schedule = {
    "nightly-self-evolution": {
        "task": "backend.core.celery_app.trigger_nightly_evolution",
        "schedule": crontab(hour=2, minute=0),  # Runs nightly at 2:00 AM UTC
    }
}

@celery_app.task
def trigger_nightly_evolution():
    """
    Asynchronous Celery task that triggers the nightly self-evolution cycle.
    Fetches negative feedback, compiles fine-tuning pairs, and invokes Replicate training.
    """
    import asyncio
    from backend.database import engine
    from backend.evolution.evolution_engine import check_and_trigger_evolution
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # We run the async process within Celery's synchronous worker thread
    async def run():
        # Create an async database session
        from sqlalchemy.orm import sessionmaker
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            await check_and_trigger_evolution(db)
            
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # In case we are running inside an existing event loop
        import nest_asyncio
        nest_asyncio.apply()
        loop.run_until_complete(run())
    else:
        loop.run_until_complete(run())
