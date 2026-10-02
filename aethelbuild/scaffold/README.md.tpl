# {{CLIENT_NAME}} — {{PROTOTYPE}} (AethelBuild prototype)

Vertical-slice AI prototype by **IIT Aethelgard (Pty) Ltd**.
Engagement: {{CLIENT_SLUG}} · tier {{TIER}} · audit ref {{AUDIT_REF}} ·
CRM ref {{CRM_REF}} · started {{DATE}}.

## Quick start
cp env.example .env   # fill from engagement vault
pip install -e ".[dev]"
ruff check src tests && pytest
uvicorn src.main:app --port 8000

## Delivery
See `/home/team/shared/delivery/aethelbuild/` (PIPELINE.md, RELEASING.md,
IP-AND-COMPLIANCE.md). Handover bundle: `scripts/build_handover.sh`.
