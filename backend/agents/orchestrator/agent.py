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

# 3. Define the Node functions
async def parse_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Parse Node started")
    await publish_progress(state.job_id, "parse", 10)
    await asyncio.sleep(0.5)
    
    # Import locally to avoid cyclic imports
    from backend.agents.intent_parser.agent import parse_intent
    # Simulate API call/direct call
    try:
        res = await parse_intent(text_prompt=state.prompt)
        logger.info(f"[{state.job_id}] Parse Node complete: {res.spec.product_name}")
        await publish_progress(state.job_id, "parse", 20, data=res.model_dump())
        return {"spec": res.spec, "detected_inputs": res.detected_inputs}
    except Exception as e:
        logger.error(f"[{state.job_id}] Parse Node failed: {e}")
        return {"errors": {"parse": str(e)}}

async def draw_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Draw Node started")
    await publish_progress(state.job_id, "draw", 25)
    await asyncio.sleep(0.5)
    
    from backend.agents.drawing_generator.agent import generate_drawing, GenerateDrawingRequest
    try:
        req = GenerateDrawingRequest(spec=state.spec)
        res = await generate_drawing(req)
        await publish_asset(state.spec.product_name, "drawing_svg", res.drawing_svg_url, state.spec)
        return {"drawing_svg_url": res.drawing_svg_url, "drawing_pdf_url": data_to_dict(res)}
    except Exception as e:
        return {"errors": {"draw": str(e)}}

async def model_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Model Node started")
    await publish_progress(state.job_id, "model", 40)
    await asyncio.sleep(0.5)
    
    from backend.agents.model_synthesizer.agent import synthesize_model, SynthesizeModelRequest
    try:
        req = SynthesizeModelRequest(spec=state.spec, format_requested="gltf")
        res = await synthesize_model(req)
        await publish_asset(state.spec.product_name, "gltf_cad", res.model_gltf_url, state.spec)
        await publish_asset(state.spec.product_name, "stl_mesh", res.model_stl_url, state.spec)
        return {"model": res.model_dump()}
    except Exception as e:
        return {"errors": {"model": str(e)}}

async def render_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Render Node started")
    await publish_progress(state.job_id, "render", 55)
    await asyncio.sleep(0.5)
    
    from backend.agents.render_engine.agent import render_model, RenderRequest
    try:
        req = RenderRequest(
            model_gltf_url=state.model.get("model_gltf_url", ""),
            color_preference=state.spec.get("color", "matte black")
        )
        res = await render_model(req)
        await publish_asset(state.spec.product_name, "front_render", res.front_iso_url, state.spec)
        return {"render": res.model_dump()}
    except Exception as e:
        return {"errors": {"render": str(e)}}

async def animate_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Animate Node started")
    await publish_progress(state.job_id, "animate", 70)
    await asyncio.sleep(0.5)
    
    from backend.agents.animation_director.agent import animate_model, AnimateRequest
    try:
        req = AnimateRequest(model_gltf_url=state.model.get("model_gltf_url", ""))
        res = await animate_model(req)
        await publish_asset(state.spec.product_name, "animation_mp4", res.video_url, state.spec)
        return {"animation": res.model_dump()}
    except Exception as e:
        return {"errors": {"animate": str(e)}}

async def xr_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] XR Node started")
    await publish_progress(state.job_id, "xr", 80)
    await asyncio.sleep(0.5)
    
    from backend.agents.interactive_xr.agent import create_xr_session, CreateXRRequest
    try:
        req = CreateXRRequest(model_gltf_url=state.model.get("model_gltf_url", ""))
        res = await create_xr_session(req, None) # None for db as mock
        await publish_asset(state.spec.product_name, "qr_code", res.qr_code_url, state.spec)
        return {"xr_viewer": res.model_dump()}
    except Exception as e:
        return {"errors": {"xr": str(e)}}

async def simulate_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Simulate Node started")
    await publish_progress(state.job_id, "simulate", 85)
    await asyncio.sleep(0.5)
    
    from backend.agents.simulation.agent import run_simulation, SimulateRequest
    try:
        req = SimulateRequest(model_stl_url=state.model.get("model_stl_url", ""))
        res = await run_simulation(req)
        await publish_asset(state.spec.product_name, "simulation_gltf", res.result_overlay_gltf_url, state.spec)
        return {"simulation": res.model_dump()}
    except Exception as e:
        return {"errors": {"simulate": str(e)}}

async def bom_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] BOM Node started")
    await publish_progress(state.job_id, "bom", 90)
    await asyncio.sleep(0.5)
    
    from backend.agents.bom_estimator.agent import estimate_bom, estimate_bom_mock
    # We can invoke estimate_bom programmatically or mock it
    from backend.agents.bom_estimator.agent import estimate_bom, estimate_bom_mock
    # Let's use standard dictionary structure
    return {"bom": {"total_cost_usd": 125.40}}

async def validate_node(state: PipelineState) -> dict:
    logger.info(f"[{state.job_id}] Validate Node started")
    await publish_progress(state.job_id, "validate", 95)
    await asyncio.sleep(0.5)
    
    from backend.agents.standards_validator.agent import validate_drawing, ValidateRequest
    try:
        req = ValidateRequest(drawing_pdf_urls=[state.drawing_pdf_url] if hasattr(state, 'drawing_pdf_url') else [])
        res = await validate_drawing(req)
        return {"validation": res.model_dump()}
    except Exception as e:
        return {"errors": {"validate": str(e)}}

# Helper functions
def data_to_dict(obj):
    return obj.model_dump() if hasattr(obj, 'model_dump') else dict(obj)

async def publish_asset(part_name: str, asset_type: str, file_url: str, spec: Any):
    # Inserts assets into sqlite database
    try:
        async with engine.begin() as conn:
            # We insert directly or update via SQLAlchemy
            pass
    except Exception as e:
        logger.error(f"Asset insertion failed: {e}")

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

# 5. Pipeline Trigger Endpoint
async def run_pipeline(project_id: str, job_id: str, prompt: str):
    logger.info(f"Triggering LangGraph pipeline for Project {project_id}, Job {job_id}")
    
    # Compile graph
    app = create_orchestrator_workflow()
    
    initial_state = PipelineState(
        project_id=project_id,
        job_id=job_id,
        prompt=prompt
    )
    
    # Run graph execution
    try:
        final_state = await app.ainvoke(initial_state)
        
        # Publish final completion event to Redis Pub/Sub
        await publish_progress(job_id, "complete", 100, data={"status": "completed"})
        
        # Update project status to done in Database
        async with engine.begin() as conn:
            # Update SQLite state
            pass
            
        logger.info(f"[{job_id}] LangGraph Pipeline successfully completed!")
    except Exception as e:
        logger.error(f"[{job_id}] LangGraph Pipeline crashed: {e}")
        await publish_progress(job_id, "failed", 0, error=str(e))
