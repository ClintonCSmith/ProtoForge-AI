from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from backend.models.models import PlanTier, ProjectStatus, AssetType, EvolutionStatus, AccessMode

# 1. UserProfile Schemas
class UserProfileBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    plan_tier: PlanTier = PlanTier.free

class UserProfileCreate(UserProfileBase):
    id: UUID  # Supplying the Supabase user ID on signup

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    plan_tier: Optional[PlanTier] = None
    stripe_customer_id: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    id: UUID
    stripe_customer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 2. Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    prompt: Optional[str] = None  # Original design prompt

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 3. ProjectVersion Schemas
class ProjectVersionBase(BaseModel):
    version_number: int
    spec: Optional[Dict[str, Any]] = None  # Decoded spec JSON
    pipeline_state: Optional[Dict[str, Any]] = None  # LangGraph state JSON

class ProjectVersionCreate(ProjectVersionBase):
    project_id: UUID

class ProjectVersionResponse(ProjectVersionBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 4. GeneratedAsset Schemas
class GeneratedAssetBase(BaseModel):
    asset_type: AssetType
    file_url: str  # Can be S3 bucket or local mock URL
    metadata_json: Optional[Dict[str, Any]] = None

class GeneratedAssetCreate(GeneratedAssetBase):
    project_id: UUID
    version_id: Optional[UUID] = None

class GeneratedAssetResponse(GeneratedAssetBase):
    id: UUID
    project_id: UUID
    version_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 5. UserFeedback Schemas
class UserFeedbackBase(BaseModel):
    agent_name: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class UserFeedbackCreate(UserFeedbackBase):
    project_id: UUID
    version_id: Optional[UUID] = None

class UserFeedbackResponse(UserFeedbackBase):
    id: UUID
    project_id: UUID
    version_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 6. EvolutionLog Schemas
class EvolutionLogBase(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]
    user_correction: Dict[str, Any]
    training_status: EvolutionStatus = EvolutionStatus.pending

class EvolutionLogCreate(EvolutionLogBase):
    pass

class EvolutionLogResponse(EvolutionLogBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 7. XRViewerToken Schemas
class XRViewerTokenBase(BaseModel):
    access_mode: AccessMode = AccessMode.read_only
    expires_at: datetime

class XRViewerTokenCreate(XRViewerTokenBase):
    project_id: UUID
    version_id: UUID

class XRViewerTokenResponse(XRViewerTokenBase):
    id: UUID
    project_id: UUID
    version_id: UUID
    token: str
    created_at: datetime

    class Config:
        from_attributes = True


# 8. Subscription Schemas
class SubscriptionBase(BaseModel):
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime

class SubscriptionCreate(SubscriptionBase):
    user_id: UUID

class SubscriptionResponse(SubscriptionBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
