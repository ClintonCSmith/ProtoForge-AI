from fastapi import APIRouter, Depends, status
from uuid import uuid4

router = APIRouter(prefix="/api-keys", tags=["api_keys"])

@router.get("")
async def get_api_keys():
    # Return user's existing API keys (mocked)
    return {
        "api_keys": [
            {"name": "production-key", "prefix": "pf_prod_...", "created_at": "2026-06-13 14:00:00"}
        ]
    }

@router.post("/rotate", status_code=status.HTTP_201_CREATED)
async def rotate_api_key():
    # Rotate keys, returning a new secret key
    new_key = f"pf_live_{uuid4().hex}{uuid4().hex}"
    return {
        "detail": "API key rotated successfully. Make sure to copy it now, as you won't be able to see it again.",
        "new_api_key": new_key
    }
