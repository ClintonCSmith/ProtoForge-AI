import logging
from backend.agents.core.celery_app import celery_app
from backend.agents.schemas import DesignSpecification, InterpretDrawingResponse

logger = logging.getLogger("DrawingInterpreterAgent")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def interpret_drawing(self, job_id: str, input_data: dict) -> dict:
    """
    Agent 3: DrawingInterpreterAgent Celery task.
    Processes drawing files (PDF/SVG/DXF) to reverse-engineer their functional
    specifications, materials, and dimensional tolerances.
    """
    logger.info(f"[{job_id}] interpret_drawing task started with input_data: {input_data}")
    try:
        drawing_url = input_data.get("drawing_url", "")
        filename = drawing_url.lower()
        
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

        response = InterpretDrawingResponse(
            spec=spec,
            extracted_notes=[
                "Tolerances ISO 2768-m apply unless otherwise specified",
                "Remove all burrs and sharp edges",
                "Surface roughness Ra 3.2 max on mounting faces"
            ],
            detected_views=["front_elevation", "side_profile", "top_plan"],
            confidence_score=0.88
        )

        logger.info(f"[{job_id}] interpret_drawing task finished successfully: {name}")
        return response.model_dump()
    except Exception as e:
        logger.error(f"[{job_id}] interpret_drawing task failed: {e}")
        self.retry(exc=e)
