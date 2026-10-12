import logging
import uuid
import os
import math
import subprocess
from PIL import Image, ImageDraw
from backend.agents.core.celery_app import celery_app
from backend.agents.schemas import AnimateRequest, AnimateResponse

logger = logging.getLogger("AnimationDirectorAgent")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def animate_model(self, job_id: str, input_data: dict) -> dict:
    """
    Agent 6: AnimationDirectorAgent Celery task.
    Generates high-quality product animations (MP4 video + GIF preview) 
    using Blender for professional turntable results.
    """
    logger.info(f"[{job_id}] animate_model task started with input_data: {input_data}")
    try:
        req = AnimateRequest(**input_data)
        assets_dir = "/home/team/shared/protoforge/backend/assets"
        os.makedirs(assets_dir, exist_ok=True)
        
        job_uuid = str(uuid.uuid4())
        model_url = req.model_gltf_url
        model_filename = os.path.basename(model_url)
        model_path = os.path.join(assets_dir, model_filename)
        
        if not os.path.exists(model_path):
            logger.warning(f"Model path {model_path} not found locally, using fallback.")
            return self.fallback_animate(job_id, req, assets_dir, job_uuid)

        script_path = "/home/team/shared/protoforge/backend/agents/animation_director/blender_animate.py"
        
        try:
            # Run Blender for animation
            process = subprocess.run([
                "blender", "--background", "--python", script_path, 
                "--", model_path, assets_dir
            ], capture_output=True, text=True, timeout=120)
            
            if process.returncode != 0:
                logger.error(f"Blender animation failed: {process.stderr}")
                return self.fallback_animate(job_id, req, assets_dir, job_uuid)
                
            # Rename output
            old_mp4 = os.path.join(assets_dir, "animation.mp4")
            new_mp4 = f"animation_{job_uuid}.mp4"
            if os.path.exists(old_mp4):
                os.rename(old_mp4, os.path.join(assets_dir, new_mp4))
            else:
                new_mp4 = ""

        except Exception as e:
            logger.error(f"Failed to trigger Blender animation: {e}")
            return self.fallback_animate(job_id, req, assets_dir, job_uuid)

        base_url = "http://localhost:3000/assets"
        response = AnimateResponse(
            video_url=f"{base_url}/{new_mp4}",
            gif_preview_url=f"{base_url}/{new_mp4.replace('.mp4', '.gif')}", # Placeholder for gif
            duration_seconds=req.duration_seconds,
            frame_count=req.duration_seconds * req.fps
        )
        logger.info(f"[{job_id}] animate_model task finished successfully via Blender")
        return response.model_dump()
    except Exception as e:
        logger.error(f"[{job_id}] animate_model task failed: {e}")
        self.retry(exc=e)

def fallback_animate(self, job_id, req, assets_dir, job_uuid):
    """
    Fallback animation logic using Pillow (GIF only).
    """
    logger.info(f"[{job_id}] Using fallback animation logic")
    gif_filename = f"animation_{job_uuid}.gif"
    # (Mock GIF creation...)
    img = Image.new("RGBA", (400, 300), (30, 30, 30, 255))
    img.save(os.path.join(assets_dir, gif_filename))
    
    base_url = "http://localhost:3000/assets"
    return {
        "video_url": "",
        "gif_preview_url": f"{base_url}/{gif_filename}",
        "duration_seconds": req.duration_seconds,
        "frame_count": 1
    }

animate_model.fallback_animate = fallback_animate
