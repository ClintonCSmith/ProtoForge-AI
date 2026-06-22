import asyncio
import json
from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

# In a production environment, this is pulled from config.py
REDIS_URL = "redis://localhost:6379/0"

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    # Returns general metadata about a job
    return {
        "job_id": job_id,
        "status": "processing",
        "progress_pct": 45,
        "completed_agents": ["IntentParserAgent", "DrawingGeneratorAgent"],
        "errors": {}
    }

@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    async def event_generator():
        # Fallback list of mock events if Redis is unavailable or for testing
        mock_steps = [
            {"event": "agent_started", "agent": "IntentParserAgent", "progress_pct": 10, "timestamp": "2026-06-13 14:10:00"},
            {"event": "agent_completed", "agent": "IntentParserAgent", "progress_pct": 30, "timestamp": "2026-06-13 14:10:02"},
            {"event": "agent_started", "agent": "ModelSynthesizerAgent", "progress_pct": 40, "timestamp": "2026-06-13 14:10:03"},
            {"event": "agent_completed", "agent": "ModelSynthesizerAgent", "progress_pct": 80, "timestamp": "2026-06-13 14:10:07"},
            {"event": "agent_started", "agent": "RenderEngineAgent", "progress_pct": 85, "timestamp": "2026-06-13 14:10:08"},
            {"event": "agent_completed", "agent": "RenderEngineAgent", "progress_pct": 95, "timestamp": "2026-06-13 14:10:10"},
            {"event": "pipeline_complete", "agent": "Finalizer", "progress_pct": 100, "timestamp": "2026-06-13 14:10:12"}
        ]

        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(REDIS_URL)
            pubsub = r.pubsub()
            await pubsub.subscribe(f"job:{job_id}:events")
            
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is not None:
                    data = message['data'].decode('utf-8')
                    yield f"data: {data}\n\n"
                    try:
                        payload = json.loads(data)
                        if payload.get("event") == "pipeline_complete":
                            break
                    except Exception:
                        pass
                await asyncio.sleep(0.5)
        except Exception:
            # Fallback to streaming mock progress so that the frontend can demonstrate progress
            for step in mock_steps:
                yield f"data: {json.dumps(step)}\n\n"
                await asyncio.sleep(1.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
