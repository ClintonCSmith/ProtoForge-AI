import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.models import Subscription, UserProfile, PlanTier

router = APIRouter(prefix="/billing", tags=["billing"])

class SubscribeRequest(BaseModel):
    plan_tier: PlanTier

@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {"tier": "free", "price_id": "free-tier-id", "price_usd": 0, "interval": "month"},
            {"tier": "starter", "price_id": "price_starter_id_123", "price_usd": 29, "interval": "month"},
            {"tier": "professional", "price_id": "price_pro_id_123", "price_usd": 99, "interval": "month"},
            {"tier": "enterprise", "price_id": "price_enterprise_id_123", "price_usd": 299, "interval": "month"},
        ]
    }

@router.post("/subscribe")
async def subscribe(data: SubscribeRequest, db: AsyncSession = Depends(get_db)):
    # Mock checkout session generation
    mock_checkout_url = f"https://checkout.stripe.com/pay/mock_session_{uuid4()}"
    return {
        "detail": "Stripe checkout session generated successfully.",
        "checkout_url": mock_checkout_url,
        "plan_tier": data.plan_tier
    }

@router.post("/cancel")
async def cancel_subscription(db: AsyncSession = Depends(get_db)):
    return {
        "detail": "Subscription cancel request received. It will remain active until the end of the billing cycle."
    }

@router.get("/portal")
async def customer_portal():
    mock_portal_url = "https://billing.stripe.com/p/session/mock_customer_portal_123"
    return {
        "portal_url": mock_portal_url
    }

@router.post("/webhooks")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    # Handle Stripe webhooks: subscription updated/deleted/payment succeeded
    payload = await request.body()
    # In real code, verify Stripe signature: stripe.Webhook.construct_event(...)
    try:
        event = json.loads(payload)
    except Exception:
        event = {"type": "customer.subscription.created", "data": {"object": {}}}

    event_type = event.get("type")
    
    # Process event types
    if event_type == "customer.subscription.created":
        # Create subscription entry in DB
        pass
    elif event_type == "customer.subscription.deleted":
        # Remove or expire subscription entry in DB
        pass

    return {"status": "success"}
