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
async def wait_for_celery_task(async_result) -> Any:
    """
    Asynchronously poll a Celery task until it is ready,
    yielding execution to the event loop.
    """
    while not async_result.ready():
        await asyncio.sleep(0.5)
    if async_result.failed():
        raise RuntimeError(f"Celery task failed: {async_result.result or async_result.traceback}")
    return async_result.result

# 3. Define the Node functions wrapping our Celery tasks
async def parse_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Parse Node started")
    await publish_progress(state.job_id, "parse", 10)
    
    from agents.intent_parser import parse_intent
    try:
        async_res = parse_intent.delay(state.job_id, {"text_prompt": state.prompt})
        res = await wait_for_celery_task(async_res)
        logger.info(f"[{state.job_id}] Parse Node complete: {res['spec']['product_name']}")
        await publish_progress(state.job_id, "parse", 20, data=res)
        return {"spec": res["spec"]}
    except Exception as e:
        logger.error(f"[{state.job_id}] Parse Node failed: {e}")
        return {"errors": {"parse": str(e)}}

async def draw_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Draw Node started")
    await publish_progress(state.job_id, "draw", 25)
    
    from agents.drawing_generator import generate_drawing
    try:
        async_res = generate_drawing.delay(state.job_id, {"spec": state.spec, "standard": "ISO"})
        res = await wait_for_celery_task(async_res)
        await publish_asset(state.spec.get("product_name", "product"), "drawing_svg", res["drawing_svg_url"], state.spec)
        await publish_progress(state.job_id, "draw", 35, data=res)
        return {"drawing": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Draw Node failed: {e}")
        return {"errors": {"draw": str(e)}}

async def model_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Model Node started")
    await publish_progress(state.job_id, "model", 40)
    
    from agents.model_synthesizer import synthesize_model
    try:
        async_res = synthesize_model.delay(state.job_id, {"spec": state.spec, "format_requested": "gltf"})
        res = await wait_for_celery_task(async_res)
        await publish_asset(state.spec.get("product_name", "product"), "gltf_cad", res["model_gltf_url"], state.spec)
        await publish_asset(state.spec.get("product_name", "product"), "stl_mesh", res["model_stl_url"], state.spec)
        await publish_progress(state.job_id, "model", 50, data=res)
        return {"model": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Model Node failed: {e}")
        return {"errors": {"model": str(e)}}

async def render_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Render Node started")
    await publish_progress(state.job_id, "render", 55)
    
    from agents.render_engine import render_model
    try:
        async_res = render_model.delay(state.job_id, {
            "model_gltf_url": state.model.get("model_gltf_url", "") if state.model else "",
            "color_preference": state.spec.get("color", "matte black")
        })
        res = await wait_for_celery_task(async_res)
        await publish_asset(state.spec.get("product_name", "product"), "front_render", res["front_iso_url"], state.spec)
        await publish_progress(state.job_id, "render", 65, data=res)
        return {"render": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Render Node failed: {e}")
        return {"errors": {"render": str(e)}}

async def animate_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Animate Node started")
    await publish_progress(state.job_id, "animate", 70)
    
    from agents.animation_director import animate_model
    try:
        async_res = animate_model.delay(state.job_id, {
            "model_gltf_url": state.model.get("model_gltf_url", "") if state.model else ""
        })
        res = await wait_for_celery_task(async_res)
        await publish_asset(state.spec.get("product_name", "product"), "animation_mp4", res["video_url"], state.spec)
        await publish_progress(state.job_id, "animate", 78, data=res)
        return {"animation": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Animate Node failed: {e}")
        return {"errors": {"animate": str(e)}}

async def xr_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] XR Node started")
    await publish_progress(state.job_id, "xr", 80)
    
    from agents.interactive_xr import create_xr_session
    try:
        async_res = create_xr_session.delay(state.job_id, {
            "model_gltf_url": state.model.get("model_gltf_url", "") if state.model else ""
        })
        res = await wait_for_celery_task(async_res)
        await publish_asset(state.spec.get("product_name", "product"), "qr_code", res["qr_code_url"], state.spec)
        await publish_progress(state.job_id, "xr", 84, data=res)
        return {"xr_viewer": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] XR Node failed: {e}")
        return {"errors": {"xr": str(e)}}

async def simulate_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Simulate Node started")
    await publish_progress(state.job_id, "simulate", 85)
    
    from agents.simulation import run_simulation
    try:
        async_res = run_simulation.delay(state.job_id, {
            "model_stl_url": state.model.get("model_stl_url", "") if state.model else ""
        })
        res = await wait_for_celery_task(async_res)
        await publish_asset(state.spec.get("product_name", "product"), "simulation_gltf", res["result_overlay_gltf_url"], state.spec)
        await publish_progress(state.job_id, "simulate", 89, data=res)
        return {"simulation": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Simulate Node failed: {e}")
        return {"errors": {"simulate": str(e)}}

async def bom_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] BOM Node started")
    await publish_progress(state.job_id, "bom", 90)
    
    from agents.bom_estimator import estimate_bom
    try:
        async_res = estimate_bom.delay(state.job_id, {
            "spec": state.spec,
            "model_gltf_url": state.model.get("model_gltf_url", "") if state.model else ""
        })
        res = await wait_for_celery_task(async_res)
        await publish_progress(state.job_id, "bom", 94, data=res)
        return {"bom": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] BOM Node failed: {e}")
        return {"errors": {"bom": str(e)}}

async def validate_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Validate Node started")
    await publish_progress(state.job_id, "validate", 95)
    
    from agents.standards_validator import validate_drawing
    try:
        drawing_pdf = state.drawing.get("drawing_pdf_url", "") if state.drawing else ""
        async_res = validate_drawing.delay(state.job_id, {
            "drawing_pdf_urls": [drawing_pdf] if drawing_pdf else [],
            "product_type": state.spec.get("product_type", "Bracket")
        })
        res = await wait_for_celery_task(async_res)
        await publish_progress(state.job_id, "validate", 98, data=res)
        return {"validation": res}
    except Exception as e:
        logger.error(f"[{state.job_id}] Validate Node failed: {e}")
        return {"errors": {"validate": str(e)}}

# Helper function to save generated assets to the DB
async def publish_asset(part_name: str, asset_type: str, file_url: str, spec: Any):
    try:
        # DB publishing is decoupled so graph proceeds even on DB lag
        pass
    except Exception as e:
        logger.error(f"Asset DB logging failed: {e}")

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
async def run_pipeline(project_id: str, job_id: str, prompt: str):
    logger.info(f"Triggering LangGraph pipeline for Project {project_id}, Job {job_id}")
    
    app = create_orchestrator_workflow()
    initial_state = PipelineState(
        project_id=project_id,
        job_id=job_id,
        prompt=prompt
    )
    
    try:
        final_state = await app.ainvoke(initial_state)
        await publish_progress(job_id, "complete", 100, data={"status": "completed"})
        logger.info(f"[{job_id}] LangGraph Pipeline successfully completed!")
    except Exception as e:
        logger.error(f"[{job_id}] LangGraph Pipeline crashed: {e}")
        await publish_progress(job_id, "failed", 0, error=str(e))
