"""
IntentParserAgent — Real AI-powered intent parsing using Anthropic Claude.
Uses the Messages API directly. Falls back to keyword matching if unavailable.
"""
import json
import logging
import os
import httpx
from backend.agents.core.celery_app import celery_app

logger = logging.getLogger("IntentParserAgent")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

EXTRACTION_PROMPT = """You are a mechanical engineering design assistant. Given a product description, extract a complete structured specification. Return ONLY valid JSON with these fields:
{
  "product_name": "string",
  "product_type": "string",
  "dimensions_mm": {"length": float, "width": float, "height": float},
  "material_preference": "string or null",
  "color": "string or null",
  "surface_finish": "string or null",
  "tolerance_class": "string or null",
  "complexity": "low|medium|high",
  "functional_features": ["string"],
  "industry": "string or null",
  "estimated_quantity": int or null,
  "confidence": float (0.0 to 1.0),
  "clarification_questions": ["string"] (if confidence < 0.7)
}
Use standard engineering materials and dimensions. Infer reasonable defaults for missing fields."""


def call_llm(prompt: str) -> dict | None:
    """Call Anthropic Claude API directly for intent extraction."""
    if not ANTHROPIC_API_KEY:
        logger.warning("No ANTHROPIC_API_KEY set — using fallback")
        return None
    
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": 1024,
                    "system": EXTRACTION_PROMPT,
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["content"][0]["text"]
            # Parse JSON from response (handle markdown-wrapped JSON)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
    except Exception as e:
        logger.error(f"Anthropic API call failed: {e}")
        return None


def fallback_parse(text_prompt: str) -> dict:
    """Simple keyword-based fallback when LLM is unavailable."""
    prompt_lower = text_prompt.lower()
    if "bottle" in prompt_lower or "holder" in prompt_lower or "cage" in prompt_lower:
        return {
            "product_name": "Water Bottle Holder", "product_type": "Bottle Cage",
            "dimensions_mm": {"length": 150, "width": 80, "height": 80},
            "material_preference": "Aluminum 6061-T6",
            "color": "Matte Black", "surface_finish": "Anodized",
            "tolerance_class": "ISO 2768-m",
            "complexity": "medium",
            "functional_features": ["Quick-release mounting", "Flexible clamp grip", "Vibration dampening"],
            "industry": "Cycling", "estimated_quantity": 100,
            "confidence": 0.45, "clarification_questions": ["Is this for road or mountain bikes?"],
        }
    elif "drone" in prompt_lower or "quad" in prompt_lower or "uav" in prompt_lower:
        return {
            "product_name": "Quadcopter Drone Frame", "product_type": "Drone Chassis",
            "dimensions_mm": {"length": 210, "width": 210, "height": 45},
            "material_preference": "Carbon Fiber",
            "color": "Raw weave", "surface_finish": "Gloss clear coat",
            "tolerance_class": "ISO 2768-f",
            "complexity": "high",
            "functional_features": ["X-configuration arms", "Vibration damping mounts", "Camera gimbal mount", "ESC mounting"],
            "industry": "Aerospace/RC", "estimated_quantity": 50,
            "confidence": 0.42, "clarification_questions": ["What frame size (mm)?"],
        }
    elif "gear" in prompt_lower:
        return {
            "product_name": "Spur Gear", "product_type": "Transmission Gear",
            "dimensions_mm": {"length": 80, "width": 80, "height": 15},
            "material_preference": "Steel 4140",
            "color": "Ground finish", "surface_finish": "Ground",
            "tolerance_class": "ISO 2768-f",
            "complexity": "medium",
            "functional_features": ["20° pressure angle", "Keyway hub", "Case hardened"],
            "industry": "Industrial Machinery", "estimated_quantity": 500,
            "confidence": 0.48, "clarification_questions": ["Number of teeth?"],
        }
    else:
        return {
            "product_name": "Custom Mechanical Part", "product_type": "General Bracket",
            "dimensions_mm": {"length": 100, "width": 50, "height": 25},
            "material_preference": "Aluminum", "color": "Silver",
            "surface_finish": "Mill", "tolerance_class": "ISO 2768-m",
            "complexity": "medium",
            "functional_features": ["Mounting holes", "Structural support"],
            "industry": "General Engineering", "estimated_quantity": 50,
            "confidence": 0.35, "clarification_questions": ["What is the primary load case?", "Any specific mounting requirements?"],
        }


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def parse_intent(self, job_id: str, input_data: dict) -> dict:
    """Real intent parser: tries OpenRouter LLM, falls back to keyword matching."""
    logger.info(f"[{job_id}] parse_intent started")
    text_prompt = input_data.get("text_prompt", "")
    
    # Try real LLM first
    result = call_llm(text_prompt) if text_prompt else None
    
    # Fallback to keyword matching if LLM unavailable
    if not result:
        logger.info(f"[{job_id}] LLM unavailable, using fallback parser")
        result = fallback_parse(text_prompt) if text_prompt else fallback_parse("default")
    
    detected = ["text"]
    if input_data.get("voice_url"):
        detected.append("voice")
    if input_data.get("sketch_url"):
        detected.append("sketch")
    
    return {
        "spec": {
            "product_name": result.get("product_name", "Part"),
            "product_type": result.get("product_type", "Bracket"),
            "dimensions": f"{result.get('dimensions_mm', {}).get('length', 100)}mm x {result.get('dimensions_mm', {}).get('width', 50)}mm x {result.get('dimensions_mm', {}).get('height', 25)}mm",
            "dimensions_mm": result.get("dimensions_mm", {"length": 100, "width": 50, "height": 25}),
            "material_preference": result.get("material_preference", "Aluminum"),
            "color": result.get("color", "Silver"),
            "surface_finish": result.get("surface_finish", "Standard"),
            "tolerance_class": result.get("tolerance_class", "ISO 2768-m"),
            "complexity": result.get("complexity", "medium"),
            "functional_features": result.get("functional_features", []),
            "industry": result.get("industry", "General Engineering"),
            "estimated_quantity": result.get("estimated_quantity", 10),
        },
        "confidence_score": result.get("confidence", 0.5),
        "detected_inputs": detected,
        "clarification_questions": result.get("clarification_questions", []),
        "raw_prompt_summary": text_prompt[:200] if text_prompt else "No text prompt",
    }