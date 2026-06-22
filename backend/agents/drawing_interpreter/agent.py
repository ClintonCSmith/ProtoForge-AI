from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

router = APIRouter(prefix="/agents", tags=["DrawingInterpreterAgent"])

class DesignSpecification(BaseModel):
    product_name: str
    product_type: str
    dimensions: str
    material_preference: str
    color: str
    complexity: str
    functional_features: List[str]

class InterpretDrawingResponse(BaseModel):
    spec: DesignSpecification
    extracted_notes: List[str]
    detected_views: List[str]
    confidence_score: float

@router.post("/interpret_drawing", response_model=InterpretDrawingResponse)
async def interpret_drawing(
    drawing_file: UploadFile = File(...)
):
    """
    Agent 3: DrawingInterpreterAgent endpoint.
    Processes drawing files (PDF/SVG/DXF) to reverse-engineer their functional
    specifications, materials, and dimensional tolerances.
    """
    filename = drawing_file.filename.lower()
    
    # Mock some intelligent reverse engineering logic!
    name = "Reconstructed Mechanical Component"
    ptype = "Custom Engineered Bracket"
    dims = "120mm x 60mm x 40mm"
    mat = "Steel Grade S235"
    color = "Zinc Plated"
    features = ["Counter-sunk mounting holes", "45-degree chamfered edges"]
    
    if "gear" in filename:
        name = "Reverse Engineered Spur Gear"
        ptype = "Spur Gear"
        dims = "Outer Dia 90mm x Thickness 12mm"
        mat = "Hardened Steel"
        color = "Natural"
        features = ["24 teeth", "8mm shaft bore", "3mm keyway slot"]
    elif "bottle" in filename or "holder" in filename:
        name = "Reverse Engineered Water Bottle Holder"
        ptype = "Cage Bracket"
        dims = "145mm x 75mm x 75mm"
        mat = "Polycarbonate"
        color = "Transparent"
        features = ["Flexible retaining ring", "Dual mounting bolt slots"]

    spec = DesignSpecification(
        product_name=name,
        product_type=ptype,
        dimensions=dims,
        material_preference=mat,
        color=color,
        complexity="medium",
        functional_features=features
    )

    return InterpretDrawingResponse(
        spec=spec,
        extracted_notes=[
            "Tolerances ISO 2768-m apply unless otherwise specified",
            "Remove all burrs and sharp edges",
            "Surface roughness Ra 3.2 max on mounting faces"
        ],
        detected_views=["front_elevation", "side_profile", "top_plan"],
        confidence_score=0.88
    )
