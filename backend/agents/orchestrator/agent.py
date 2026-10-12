import asyncio
import json
import logging
import os
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import redis.asyncio as aioredis
from langgraph.graph import StateGraph, END

# Import async db session for saving progress
from backend.database import engine
from backend.models.models import Project, ProjectVersion, GeneratedAsset, ProjectStatus
from backend.agents.core.celery_app import celery_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrchestratorAgent")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 1. Define LangGraph state schema
class PipelineState(BaseModel):
    project_id: str
    job_id: str
    prompt: str
    spec: Optional[dict] = None
    drawing: Optional[dict] = None
    model: Optional[dict] = None
    render: Optional[dict] = None
    animation: Optional[dict] = None
    xr_viewer: Optional[dict] = None
    simulation: Optional[dict] = None
    bom: Optional[dict] = None
    validation: Optional[dict] = None
    current_stage: str = "init"
    progress_pct: int = 0
    errors: Dict[str, str] = {}
    retries: Dict[str, int] = {}

# 2. Redis Pub/Sub Helper to send live progress updates to SSE
async def publish_progress(job_id: str, stage: str, progress_pct: int, data: Optional[dict] = None, error: Optional[str] = None):
    try:
        redis_client = aioredis.from_url(REDIS_URL)
        event_data = {
            "job_id": job_id,
            "stage": stage,
            "progress_pct": progress_pct,
            "status": "failed" if error else ("running" if progress_pct < 100 and stage != "complete" else "done"),
            "data": data,
            "error": error,
            "estimated_time_remaining": max(0, int((100 - progress_pct) * 0.4))  # countdown estimate
        }
        await redis_client.publish(f"job:{job_id}:events", json.dumps(event_data))
        await redis_client.close()
    except Exception as e:
        logger.error(f"Failed to publish progress to Redis: {e}")

# Helper to wait for Celery task asynchronously without blocking the loop
async def wait_for_celery_task(async_result, timeout=300) -> Any:
    """
    Asynchronously poll a Celery task until it is ready,
    yielding execution to the event loop.
    """
    start_time = asyncio.get_event_loop().time()
    while not async_result.ready():
        if asyncio.get_event_loop().time() - start_time > timeout:
            raise TimeoutError("Celery task timed out")
        await asyncio.sleep(1.0)
    
    if async_result.failed():
        # Check if it was a real failure or a revoked task
        state = async_result.state
        raise RuntimeError(f"Celery task failed with state {state}: {async_result.result}")
    
    return async_result.result

async def execute_task_with_retry(task_func, job_id, *args, max_retries=3):
    """
    Helper to execute a celery task with exponential backoff retries at the orchestrator level.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            async_res = task_func.delay(job_id, *args)
            return await wait_for_celery_task(async_res)
        except Exception as e:
            last_error = e
            wait_time = (2 ** attempt) + 1
            logger.warning(f"Task {task_func.__name__} attempt {attempt+1} failed: {e}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
    raise last_error

# 3. Define the Node functions wrapping our Celery tasks
async def parse_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Parse Node started")
    await publish_progress(state.job_id, "parse", 10)
    
    from backend.agents.intent_parser.tasks import parse_intent
    try:
        res = await execute_task_with_retry(parse_intent, state.job_id, {"text_prompt": state.prompt})
        await publish_progress(state.job_id, "parse", 20, data=res)
        return {"spec": res["spec"]}
    except Exception as e:
        logger.error(f"[{state.job_id}] Parse Node failed after retries: {e}")
        return {"errors": {"parse": str(e)}}

async def draw_node(state: PipelineState) -> dict:
    if "parse" in state.errors:
        return {} # Skip if core dependency failed
        
    logger.info(f"[{state.job_id}] Draw Node started")
    await publish_progress(state.job_id, "draw", 25)
    
    from backend.agents.drawing_generator.tasks import generate_drawing
    try:
        res = await execute_task_with_retry(generate_drawing, state.job_id, {"spec": state.spec, "standard": "ISO"})
        await publish_progress(state.job_id, "draw", 35, data=res)
        return {"drawing": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Draw Node failed: {e}")
        return {"errors": {"draw": str(e)}}

async def model_node(state: PipelineState) -> dict:
    if "parse" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] Model Node started")
    await publish_progress(state.job_id, "model", 40)
    
    from backend.agents.model_synthesizer.tasks import synthesize_model
    try:
        res = await execute_task_with_retry(synthesize_model, state.job_id, {"spec": state.spec, "format_requested": "gltf"})
        await publish_progress(state.job_id, "model", 50, data=res)
        return {"model": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Model Node failed: {e}")
        return {"errors": {"model": str(e)}}

async def render_node(state: PipelineState) -> dict:
    if not state.model or "model" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] Render Node started")
    await publish_progress(state.job_id, "render", 55)
    
    from backend.agents.render_engine.tasks import render_model
    try:
        res = await execute_task_with_retry(render_model, state.job_id, {
            "model_gltf_url": state.model.get("model_gltf_url", ""),
            "color_preference": state.spec.get("color", "matte black") if state.spec else "matte black"
        })
        await publish_progress(state.job_id, "render", 65, data=res)
        return {"render": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Render Node failed: {e}")
        return {"errors": {"render": str(e)}}

async def animate_node(state: PipelineState) -> dict:
    if not state.model or "model" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] Animate Node started")
    await publish_progress(state.job_id, "animate", 70)
    
    from backend.agents.animation_director.tasks import animate_model
    try:
        res = await execute_task_with_retry(animate_model, state.job_id, {
            "model_gltf_url": state.model.get("model_gltf_url", "")
        })
        await publish_progress(state.job_id, "animate", 78, data=res)
        return {"animation": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Animate Node failed: {e}")
        return {"errors": {"animate": str(e)}}

async def xr_node(state: PipelineState) -> dict:
    if not state.model or "model" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] XR Node started")
    await publish_progress(state.job_id, "xr", 80)
    
    from backend.agents.interactive_xr.tasks import create_xr_session
    try:
        res = await execute_task_with_retry(create_xr_session, state.job_id, {
            "model_gltf_url": state.model.get("model_gltf_url", "")
        })
        await publish_progress(state.job_id, "xr", 84, data=res)
        return {"xr_viewer": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] XR Node failed: {e}")
        return {"errors": {"xr": str(e)}}

async def simulate_node(state: PipelineState) -> dict:
    if not state.model or "model" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] Simulate Node started")
    await publish_progress(state.job_id, "simulate", 85)
    
    from backend.agents.simulation.tasks import run_simulation
    try:
        res = await execute_task_with_retry(run_simulation, state.job_id, {
            "model_stl_url": state.model.get("model_stl_url", "")
        })
        await publish_progress(state.job_id, "simulate", 89, data=res)
        return {"simulation": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Simulate Node failed: {e}")
        return {"errors": {"simulate": str(e)}}

async def bom_node(state: PipelineState) -> dict:
    if not state.spec or "parse" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] BOM Node started")
    await publish_progress(state.job_id, "bom", 90)
    
    from backend.agents.bom_estimator.tasks import estimate_bom
    try:
        res = await execute_task_with_retry(estimate_bom, state.job_id, {
            "spec": state.spec,
            "model_gltf_url": state.model.get("model_gltf_url", "") if state.model else ""
        })
        await publish_progress(state.job_id, "bom", 94, data=res)
        return {"bom": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] BOM Node failed: {e}")
        return {"errors": {"bom": str(e)}}

async def validate_node(state: PipelineState) -> dict:
    if not state.drawing or "draw" in state.errors:
        return {}
        
    logger.info(f"[{state.job_id}] Validate Node started")
    await publish_progress(state.job_id, "validate", 95)
    
    from backend.agents.standards_validator.tasks import validate_drawing
    try:
        drawing_pdf = state.drawing.get("drawing_pdf_url", "")
        res = await execute_task_with_retry(validate_drawing, state.job_id, {
            "drawing_pdf_urls": [drawing_pdf] if drawing_pdf else [],
            "product_type": state.spec.get("product_type", "Bracket") if state.spec else "Bracket"
        })
        await publish_progress(state.job_id, "validate", 98, data=res)
        return {"validation": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Validate Node failed: {e}")
        return {"errors": {"validate": str(e)}}

# 4. Construct LangGraph Workflow
def create_orchestrator_workflow() -> StateGraph:
    workflow = StateGraph(PipelineState)
    
    # Register Nodes
    workflow.add_node("parse", parse_node)
    workflow.add_node("draw", draw_node)
    workflow.add_node("model", model_node)
    workflow.add_node("render", render_node)
    workflow.add_node("animate", animate_node)
    workflow.add_node("xr", xr_node)
    workflow.add_node("simulate", simulate_node)
    workflow.add_node("bom", bom_node)
    workflow.add_node("validate", validate_node)
    
    # Establish sequential flow
    # We use edges that allow continuing even if previous nodes added errors to the state.
    # The nodes themselves check state.errors for critical dependencies.
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "draw")
    workflow.add_edge("draw", "model")
    workflow.add_edge("model", "render")
    workflow.add_edge("render", "animate")
    workflow.add_edge("animate", "xr")
    workflow.add_edge("xr", "simulate")
    workflow.add_edge("simulate", "bom")
    workflow.add_edge("bom", "validate")
    workflow.add_edge("validate", END)
    
    return workflow.compile()

# 5. Pipeline Trigger Function
@celery_app.task(bind=True, max_retries=1)
def run_pipeline_task(self, project_id: str, job_id: str, prompt: str):
    """
    Agent 12: OrchestratorAgent Celery task.
    Entry point for the LangGraph design pipeline.
    """
    logger.info(f"Triggering LangGraph pipeline for Project {project_id}, Job {job_id}")
    
    # We run the async LangGraph workflow within Celery's synchronous thread
    import asyncio
    
    async def _run():
        app = create_orchestrator_workflow()
        initial_state = PipelineState(
            project_id=project_id,
            job_id=job_id,
            prompt=prompt
        )
        try:
            # Persistent job state can be saved to PG here if needed
            # For now we use the LangGraph in-memory state during the run
            final_state = await app.ainvoke(initial_state)
            
            # Check for total failure
            if len(final_state["errors"]) > 3: # Arbitrary threshold for "failed" pipeline
                 await publish_progress(job_id, "failed", 0, error="Too many pipeline stage failures.")
            else:
                 await publish_progress(job_id, "complete", 100, data={"status": "completed", "errors": final_state["errors"]})
            
            logger.info(f"[{job_id}] LangGraph Pipeline finished with {len(final_state['errors'])} errors")
        except Exception as e:
            logger.error(f"[{job_id}] LangGraph Pipeline crashed: {e}")
            await publish_progress(job_id, "failed", 0, error=str(e))
            raise e

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()
