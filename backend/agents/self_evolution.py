import logging
import asyncio
from agents.core.celery_app import celery_app

logger = logging.getLogger("SelfEvolutionEngine")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_evolution_pipeline(self):
    """
    Agent 12: SelfEvolutionEngine Celery task.
    Runs nightly at 02:00 UTC. Collects negative feedback, compiles fine-tuning pairs,
    and invokes Replicate training.
    """
    logger.info("Triggering Self-Evolution Pipeline Celery task...")
    
    # We run the async process within Celery's synchronous worker thread
    async def run():
        # Lazy imports to avoid cyclic dependencies
        from backend.database import engine
        from backend.evolution.evolution_engine import check_and_trigger_evolution
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            result = await check_and_trigger_evolution(db)
            logger.info(f"Nightly evolution run complete. Result run_id: {result}")
            return result
            
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(run())
        else:
            return loop.run_until_complete(run())
    except Exception as e:
        logger.error(f"Self-Evolution Pipeline failed: {e}")
        self.retry(exc=e)
