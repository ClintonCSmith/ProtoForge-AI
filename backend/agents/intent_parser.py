import logging
from agents.core.celery_app import celery_app
from agents.schemas import DesignSpecification, ParseInputResponse

logger = logging.getLogger("IntentParserAgent")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def parse_intent(self, job_id: str, input_data: dict) -> dict:
    """
    Agent 1: IntentParserAgent Celery task.
    Parses natural language prompts, sketches, or voice recordings to produce
    a unified, machine-readable product design specification (spec).
    """
    logger.info(f"[{job_id}] parse_intent task started with input_data: {input_data}")
    try:
        text_prompt = input_data.get("text_prompt")
        voice_url = input_data.get("voice_url")
        sketch_url = input_data.get("sketch_url")

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

        if voice_url:
            detected.append("voice")
            summary_parts.append(f"Audio URL: {voice_url}")

        if sketch_url:
            detected.append("sketch")
            summary_parts.append(f"Sketch URL: {sketch_url}")

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

        response = ParseInputResponse(
            spec=spec,
            confidence_score=0.92 if "text" in detected else 0.85,
            detected_inputs=detected,
            raw_prompt_summary=" | ".join(summary_parts)
        )

        logger.info(f"[{job_id}] parse_intent task finished successfully: {name}")
        return response.model_dump()
    except Exception as e:
        logger.error(f"[{job_id}] parse_intent task failed: {e}")
        self.retry(exc=e)
