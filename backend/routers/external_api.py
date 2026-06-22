from fastapi import APIRouter, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter(prefix="/api/v1", tags=["external_api"])

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

class ExternalGenerateRequest(BaseModel):
    prompt: str

@router.post("/generate")
async def external_generate(data: ExternalGenerateRequest, api_key: str = Security(api_key_header)):
    # Validate API key
    if api_key != "mock-api-key-12345":
        # Accept any for simplicity of demonstration, but let's assert non-empty
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials"
            )
            
    mock_job_id = str(uuid4())
    return {
        "detail": "Generation job spawned successfully.",
        "job_id": mock_job_id
    }

@router.get("/jobs/{job_id}")
async def get_external_job_status(job_id: str, api_key: str = Security(api_key_header)):
    return {
        "job_id": job_id,
        "status": "complete",
        "progress_pct": 100,
        "assets": {
            "gltf_url": "https://s3.amazonaws.com/protoforge/mock_drone.gltf",
            "step_url": "https://s3.amazonaws.com/protoforge/mock_drone.step",
            "stl_url": "https://s3.amazonaws.com/protoforge/mock_drone.stl"
        }
    }
