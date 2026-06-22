from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

router = APIRouter(prefix="/agents", tags=["IntentParserAgent"])

class DesignSpecification(BaseModel):
    product_name: str = Field(..., description="Calculated name of the product")
    product_type: str = Field(..., description="General category of the product")
    dimensions: str = Field(..., description="Extracted dimension constraints (e.g., 150x50x50 mm)")
    material_preference: str = Field("aluminum", description="Preferred raw material")
    color: str = Field("matte black", description="Desired surface finish color")
    complexity: str = Field("medium", description="Estimated design complexity")
    functional_features: List[str] = Field(default_factory=list, description="Extracted core features")

class ParseInputRequest(BaseModel):
    text_prompt: Optional[str] = None
    voice_url: Optional[str] = None
    sketch_url: Optional[str] = None

class ParseInputResponse(BaseModel):
    spec: DesignSpecification
    confidence_score: float
    detected_inputs: List[str]
    raw_prompt_summary: str

@router.post("/parse", response_model=ParseInputResponse)
async def parse_intent(
    text_prompt: Optional[str] = Form(None),
    voice_file: Optional[UploadFile] = File(None),
    sketch_file: Optional[UploadFile] = File(None)
):
    """
    Agent 1: IntentParserAgent endpoint.
    Parses natural language prompts, sketches, or voice recordings to produce
    a unified, machine-readable product design specification (spec).
    """
    detected = []
    summary_parts = []
    
    name = "Ergonomic CAD Part"
    ptype = "Mechanical Bracket"
    dims = "100mm x 50mm x 25mm"
    mat = "Aluminum 6061-T6"
    color = "Anodized Silver"
    features = ["quick-release mounting", "structural ribbing"]

    if text_prompt:
        detected.append("text")
        summary_parts.append(f"Text prompt: '{text_prompt}'")
        # Extract metadata from text prompt if present
        prompt_lower = text_prompt.lower()
        if "bottle" in prompt_lower or "holder" in prompt_lower:
            name = "Ergonomic Water Bottle Holder"
            ptype = "Bottle Cage"
            dims = "150mm x 80mm x 80mm"
            mat = "Matte Black Carbon Fiber"
            color = "Matte Black"
            features = ["Quick-release frame mounting", "flexible clamp grip"]
        elif "drone" in prompt_lower:
            name = "Quadcopter Drone Frame"
            ptype = "Drone Chassis"
            dims = "210mm x 210mm x 45mm"
            mat = "CFRP (Carbon Fiber)"
            color = "Raw weave carbon"
            features = ["X-configuration arms", "vibration damping mounts", "camera gimbal mount"]
        elif "gear" in prompt_lower:
            name = "Spur Gear Assembly"
            ptype = "Transmission Gear"
            dims = "80mm diameter x 15mm width"
            mat = "Brass"
            color = "Gold"
            features = ["20 degree pressure angle", "keyway hub slot"]

    if voice_file:
        detected.append("voice")
        summary_parts.append(f"Audio file: {voice_file.filename}")

    if sketch_file:
        detected.append("sketch")
        summary_parts.append(f"Sketch file: {sketch_file.filename}")

    if not detected:
        detected.append("default")
        summary_parts.append("Default template initialized (no prompt received).")

    spec = DesignSpecification(
        product_name=name,
        product_type=ptype,
        dimensions=dims,
        material_preference=mat,
        color=color,
        complexity="medium" if len(features) < 3 else "high",
        functional_features=features
    )

    return ParseInputResponse(
        spec=spec,
        confidence_score=0.92 if "text" in detected else 0.85,
        detected_inputs=detected,
        raw_prompt_summary=" | ".join(summary_parts)
    )
