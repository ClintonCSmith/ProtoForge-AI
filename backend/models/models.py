import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    Boolean,
    ForeignKey, 
    DateTime, 
    Text, 
    Enum as SqlEnum,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base

# Enums
class PlanTier(str, enum.Enum):
    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"

class ProjectStatus(str, enum.Enum):
    draft = "draft"
    processing = "processing"
    complete = "complete"
    failed = "failed"

class AssetType(str, enum.Enum):
    cad_step = "cad_step"
    cad_stl = "cad_stl"
    cad_obj = "cad_obj"
    cad_gltf = "cad_gltf"
    drawing_pdf = "drawing_pdf"
    drawing_svg = "drawing_svg"
    drawing_dxf = "drawing_dxf"
    render_hero = "render_hero"
    render_angle = "render_angle"
    animation_mp4 = "animation_mp4"
    simulation_mesh = "simulation_mesh"
    simulation_report = "simulation_report"
    bom_csv = "bom_csv"

class EvolutionStatus(str, enum.Enum):
    pending = "pending"
    processed = "processed"
    skipped = "skipped"

class AccessMode(str, enum.Enum):
    read_only = "read_only"
    interactive_sandbox = "interactive_sandbox"


# Models
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    plan_tier = Column(SqlEnum(PlanTier), default=PlanTier.free, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SqlEnum(ProjectStatus), default=ProjectStatus.draft, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserProfile", back_populates="projects")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("GeneratedAsset", back_populates="project", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="project", cascade="all, delete-orphan")
    xr_tokens = relationship("XRViewerToken", back_populates="project", cascade="all, delete-orphan")


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    spec = Column(JSONB, nullable=True)  # Stores extracted/parsed product specification
    pipeline_state = Column(JSONB, nullable=True)  # Stores LangGraph orchestrator state
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="versions")
    assets = relationship("GeneratedAsset", back_populates="version", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="version", cascade="all, delete-orphan")
    xr_tokens = relationship("XRViewerToken", back_populates="version", cascade="all, delete-orphan")


class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("project_versions.id", ondelete="CASCADE"), nullable=True, index=True)
    asset_type = Column(SqlEnum(AssetType), nullable=False)
    file_url = Column(String(1024), nullable=False)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="assets")
    version = relationship("ProjectVersion", back_populates="assets")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("project_versions.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_name = Column(String(255), nullable=False)  # Name of the agent the feedback is for
    rating = Column(Integer, nullable=False)  # Rating between 1 and 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="feedback")
    version = relationship("ProjectVersion", back_populates="feedback")


class EvolutionLog(Base):
    __tablename__ = "evolution_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String(255), nullable=False, index=True)
    input_data = Column(JSONB, nullable=False)  # The original inputs given to the agent
    user_correction = Column(JSONB, nullable=False)  # The manual corrections made by user
    training_status = Column(SqlEnum(EvolutionStatus), default=EvolutionStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class XRViewerToken(Base):
    __tablename__ = "xr_viewer_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("project_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    access_mode = Column(SqlEnum(AccessMode), default=AccessMode.read_only, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="xr_tokens")
    version = relationship("ProjectVersion", back_populates="xr_tokens")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    plan = Column(String(50), nullable=False, default="free")
    payfast_subscription_id = Column(String(255), nullable=True, unique=True, index=True)
    payfast_token = Column(String(255), nullable=True)
    status = Column(String(100), nullable=False, default="pending")
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserProfile", back_populates="subscriptions")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    plan_tier = Column(String(50), nullable=False)
    amount_zar = Column(Integer, nullable=False)
    currency = Column(String(3), default="ZAR")
    status = Column(String(20), default="pending")
    payment_method = Column(String(50), nullable=True)
    payfast_payment_id = Column(String(255), nullable=True)
    pdf_url = Column(String(1024), nullable=True)
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserProfile")
    subscription = relationship("Subscription")
