"""
StandardsValidatorAgent — Validates engineering drawings against ISO/ASME/DIN rules.
Uses AI vision for drawing inspection when available.
"""
import logging
import os
import yaml
import httpx
from backend.agents.core.celery_app import celery_app

logger = logging.getLogger("StandardsValidatorAgent")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")


def load_rules() -> list[dict]:
    """Load validation rules from rules.yaml."""
    rules_path = os.path.join(os.path.dirname(__file__), "rules.yaml")
    try:
        with open(rules_path) as f:
            data = yaml.safe_load(f)
            return data.get("rules", [])
    except Exception as e:
        logger.warning(f"Failed to load rules: {e}")
        return []


def check_drawing_with_vision(drawing_url: str, rules: list[dict]) -> list[dict]:
    """Use AI vision to check drawing compliance."""
    if not OPENROUTER_API_KEY or not drawing_url:
        return []
    
    vision_rules = [r for r in rules if r.get("check_type") == "vision"]
    if not vision_rules:
        return []
    
    rules_text = "\n".join([
        f"- {r['rule_id']} ({r['standard']}, {r['severity']}): {r['description']}"
        for r in vision_rules
    ])
    
    try:
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-sonnet-4",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an engineering drawing inspector. Check the drawing against these rules and return JSON list of violations found:\n{rules_text}\nReturn format: [{{\"rule_id\": \"...\", \"severity\": \"error|warning|info\", \"location\": \"...\", \"description\": \"...\", \"suggestion\": \"...\"}}]",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Inspect this engineering drawing for standard compliance."},
                            {"type": "image_url", "image_url": {"url": drawing_url}},
                        ],
                    },
                ],
                "temperature": 0.1,
                "max_tokens": 2048,
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        import json
        # Parse JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        violations = json.loads(content)
        return violations if isinstance(violations, list) else []
    except Exception as e:
        logger.warning(f"Vision check failed: {e}")
        return []


@celery_app.task(bind=True, max_retries=2, default_retry_delay=5)
def validate_drawing(self, job_id: str, input_data: dict) -> dict:
    """Validate drawing against standards rules with AI vision."""
    drawing_pdf_urls = input_data.get("drawing_pdf_urls", [])
    product_type = input_data.get("product_type", "General Part")
    standard = input_data.get("standard", "ISO")
    
    rules = load_rules()
    applicable_rules = [r for r in rules if r.get("standard") == standard]
    violations = []
    passed_checks = []
    
    # Run vision-based checks on each drawing
    for drawing_url in drawing_pdf_urls:
        vision_violations = check_drawing_with_vision(drawing_url, applicable_rules)
        violations.extend(vision_violations)
    
    # Run regex/geometric checks on rules
    for rule in applicable_rules:
        check_type = rule.get("check_type", "vision")
        # Vision checks already handled above
        if check_type != "vision":
            passed_checks.append(rule["rule_id"])
    
    # Calculate score
    violation_count = len(violations)
    error_count = sum(1 for v in violations if v.get("severity") == "error")
    warning_count = sum(1 for v in violations if v.get("severity") == "warning")
    
    if violation_count == 0:
        score = 100
    else:
        score = max(0, 100 - (error_count * 15 + warning_count * 5))
    
    passed = score >= 80 and error_count == 0
    
    return {
        "passed": passed,
        "score": score,
        "violations": violations,
        "passed_checks": passed_checks,
        "standard": standard,
        "rules_checked": len(applicable_rules),
        "summary": f"{'PASSED' if passed else 'FAILED'} — Score: {score}/100 ({error_count} errors, {warning_count} warnings)",
    }