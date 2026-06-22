from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.models import XRViewerToken, AccessMode

router = APIRouter(prefix="/viewers", tags=["viewer"])

class CreateTokenRequest(BaseModel):
    project_id: UUID
    version_id: UUID
    access_mode: AccessMode = AccessMode.read_only

@router.get("/view/{token}")
async def get_viewer_session(token: str, db: AsyncSession = Depends(get_db)):
    # Returns 3D assets linked to the token for the WebXR app
    return {
        "token": token,
        "project_id": str(uuid4()),
        "version_id": str(uuid4()),
        "access_mode": "read_only",
        "gltf_url": "https://s3.amazonaws.com/protoforge/mock_drone.gltf",
        "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }

@router.post("")
async def create_viewer_token(data: CreateTokenRequest, db: AsyncSession = Depends(get_db)):
    mock_token = f"tok_{uuid4().hex}"
    return {
        "token": mock_token,
        "access_mode": data.access_mode,
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }

@router.get("/{token}/stats")
async def get_viewer_stats(token: str):
    return {
        "token": token,
        "views_count": 42,
        "last_accessed": datetime.utcnow().isoformat(),
        "average_session_seconds": 124
    }
