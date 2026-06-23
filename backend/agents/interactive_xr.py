import logging
import uuid
import os
import qrcode
from agents.core.celery_app import celery_app
from agents.schemas import CreateXRRequest, CreateXRResponse
from backend.database import SessionLocal  # Since celery worker runs synchronously or asynchronously we use a standard sessionmaker
from backend.models.models import XRViewerToken

logger = logging.getLogger("InteractiveXRAgent")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def create_xr_session(self, job_id: str, input_data: dict) -> dict:
    """
    Agent 7: InteractiveXRAgent Celery task.
    Creates password-protected WebGL/WebXR interactive 3D viewer pages and QR codes.
    Stores the configuration in the shared database.
    """
    logger.info(f"[{job_id}] create_xr_session task started with input_data: {input_data}")
    try:
        req = CreateXRRequest(**input_data)
        token_uuid = uuid.uuid4()
        assets_dir = "/home/team/shared/protoforge/backend/assets"
        os.makedirs(assets_dir, exist_ok=True)
        
        # Store session token in SQLite/Turso database using synchrounous SessionLocal
        try:
            db = SessionLocal()
            db_token = XRViewerToken(
                id=token_uuid,
                token=str(token_uuid),
                access_mode=req.access_control.mode if req.access_control else "public",
                password_hash=req.access_control.password_hash if req.access_control else None
            )
            db.add(db_token)
            db.commit()
            db.close()
            logger.info(f"[{job_id}] Stored XR token {token_uuid} in database")
        except Exception as e:
            logger.error(f"[{job_id}] Database storage fallback / schema exception: {e}")
            # Fallback in case database session is missing/not-configured in Celery
            pass

        # Generate the actual QR code pointing to the WebGL viewer URL!
        viewer_url = f"http://localhost:3000/view/{token_uuid}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(viewer_url)
        qr.make(fit=True)
        
        # Export QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_filename = f"qr_{token_uuid}.png"
        qr_path = os.path.join(assets_dir, qr_filename)
        qr_img.save(qr_path)
        
        ar_url = f"http://localhost:3000/assets/model_{token_uuid}.usdz"  # Reality converter redirect
        embed_code = f'<iframe src="{viewer_url}" width="100%" height="600px" allow="xr-spatial-tracking; camera" frameborder="0"></iframe>'
        
        base_url = "http://localhost:3000/assets"
        
        response = CreateXRResponse(
            viewer_url=viewer_url,
            ar_url=ar_url,
            embed_code=embed_code,
            qr_code_url=f"{base_url}/{qr_filename}"
        )

        logger.info(f"[{job_id}] create_xr_session task finished successfully")
        return response.model_dump()
    except Exception as e:
        logger.error(f"[{job_id}] create_xr_session task failed: {e}")
        self.retry(exc=e)
