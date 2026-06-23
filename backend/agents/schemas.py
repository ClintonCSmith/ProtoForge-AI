from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Shared Core Specification
class DesignSpecification(BaseModel):
    product_name: str = Field(..., description="Calculated name of the product")
    product_type: str = Field(..., description="General category of the product")
    dimensions: str = Field(..., description="Extracted dimension constraints (e.g., 150x50x50 mm)")
    material_preference: str = Field("aluminum", description="Preferred raw material")
    color: str = Field("matte black", description="Desired surface finish color")
    complexity: str = Field("medium", description="Estimated design complexity")
    functional_features: List[str] = Field(default_factory=list, description="Extracted core features")

# Agent 1 — IntentParser
class ParseInputRequest(BaseModel):
    text_prompt: Optional[str] = None
    voice_url: Optional[str] = None
    sketch_url: Optional[str] = None

class ParseInputResponse(BaseModel):
    spec: DesignSpecification
    confidence_score: float
    detected_inputs: List[str]
    raw_prompt_summary: str

# Agent 2 — DrawingGenerator
class GenerateDrawingRequest(BaseModel):
    spec: DesignSpecification
    standard: str = Field("ISO", description="Engineering standard: ISO, ASME_Y14, or DIN")

class GenerateDrawingResponse(BaseModel):
    drawing_pdf_url: str
    drawing_dxf_url: str
    drawing_svg_url: str
    drawing_svg_content: str
    standard_applied: str

# Agent 3 — DrawingInterpreter
class InterpretDrawingResponse(BaseModel):
    spec: DesignSpecification
    extracted_notes: List[str]
    detected_views: List[str]
    confidence_score: float

# Agent 4 — ModelSynthesizer
class SynthesizeModelRequest(BaseModel):
    spec: DesignSpecification
    format_requested: str = Field("gltf", description="step, stl, or gltf")

class SynthesizeModelResponse(BaseModel):
    model_gltf_url: str
    model_stl_url: str
    model_step_url: str
    bounding_box: List[float]
    volume_cm3: float
    surface_area_cm2: float

# Agent 5 — RenderEngine
class RenderRequest(BaseModel):
    model_gltf_url: str
    material_settings: Optional[str] = "aluminum"
    color_preference: Optional[str] = "matte black"
    lighting_preset: Optional[str] = "studio"

class RenderResponse(BaseModel):
    front_iso_url: str
    rear_iso_url: str
    top_url: str
    left_url: str
    right_url: str
    camera_angles_rendered: List[str]

# Agent 6 — AnimationDirector
class AnimateRequest(BaseModel):
    model_gltf_url: str
    material_settings: Optional[str] = "aluminum"
    animation_type: str = Field("turntable", description="turntable, exploded, operational, or cinematic")
    duration_seconds: int = 4
    fps: int = 15

class AnimateResponse(BaseModel):
    video_url: str
    gif_preview_url: str
    duration_seconds: int
    frame_count: int

# Agent 7 — InteractiveXR
class BrandingSettings(BaseModel):
    company_name: Optional[str] = "ProtoForge AI"
    logo_url: Optional[str] = "http://localhost:3000/logo.png"
    accent_color: Optional[str] = "#38bdf8"

class AccessControlSettings(BaseModel):
    mode: str = Field("public", description="public, password, or private")
    password_hash: Optional[str] = None

class CreateXRRequest(BaseModel):
    model_gltf_url: str
    branding: Optional[BrandingSettings] = Field(default_factory=BrandingSettings)
    access_control: Optional[AccessControlSettings] = Field(default_factory=AccessControlSettings)
    features: Optional[List[str]] = Field(default_factory=list)

class CreateXRResponse(BaseModel):
    viewer_url: str
    ar_url: str
    embed_code: str
    qr_code_url: str

# Agent 8 — Simulation
class LoadCondition(BaseModel):
    type: str = Field("pressure", description="pressure, force, or moment")
    magnitude: float = Field(..., description="Load magnitude in Newtons or MPa")
    direction: List[float] = Field(default_factory=lambda: [0.0, 0.0, -1.0])
    surface_id: Optional[str] = "top_face"

class MaterialProperties(BaseModel):
    youngs_modulus_gpa: float = 200.0
    poisson_ratio: float = 0.29
    density_kg_m3: float = 7850.0
    yield_strength_mpa: float = 250.0

class SimulateRequest(BaseModel):
    model_stl_url: str
    simulation_type: str = Field("fea_stress", description="fea_stress, fea_displacement, or thermal")
    material_properties: Optional[MaterialProperties] = Field(default_factory=MaterialProperties)
    load_conditions: Optional[List[LoadCondition]] = Field(default_factory=list)

class SimulateResponse(BaseModel):
    result_overlay_gltf_url: str
    result_image_url: str
    max_stress_mpa: float
    max_displacement_mm: float
    safety_factor: float
    hotspot_coordinates: List[float]
    summary: str

# Agent 9 — StandardsValidator
class Violation(BaseModel):
    rule_id: str
    severity: str
    location: str
    description: str
    suggestion: str

class ValidateRequest(BaseModel):
    drawing_pdf_urls: List[str]
    standard: str = Field("ISO", description="ISO, ASME_Y14, or DIN")
    product_type: Optional[str] = "Bracket"

class ValidateResponse(BaseModel):
    passed: bool
    score: int
    violations: List[Violation]
    passed_checks: List[str]

# Agent 10 — BOMEstimator
class BOMItem(BaseModel):
    part_number: str
    description: str
    material: str
    qty: int
    unit: str
    unit_cost_usd: float
    total_cost_usd: float
    supplier_options: List[str]

class EstimateBOMRequest(BaseModel):
    spec: DesignSpecification
    model_gltf_url: str
    quantity: int = Field(1, description="Production volume size")
    currency: str = Field("USD", description="Currency preset: USD, EUR, GBP, or ZAR")

class EstimateBOMResponse(BaseModel):
    bom: List[BOMItem]
    total_material_cost_usd: float
    estimated_manufacturing_cost_usd: float
    tooling_cost_estimate_usd: float
    estimated_unit_cost_usd: float
    exchange_rate: float
    currency: str
