import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.models import Subscription, UserProfile, PlanTier, Invoice
from backend.services.payments.payfast import (
    PLANS,
    BUSINESS_BANKING,
    create_subscription_url,
    create_once_off_payment_url,
    validate_ipn,
    verify_plan_access,
    generate_invoice_html,
)

router = APIRouter(prefix="/billing", tags=["billing"])


async def get_current_user(request: Request) -> UUID:
    """
    Extract the current user ID from the JWT token.
    (Simplified — in production, decode the Supabase JWT.)
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    # In production: decode JWT, extract sub
    # For now: return a placeholder
    return UUID("00000000-0000-0000-0000-000000000000")


class SubscribeRequest(BaseModel):
    plan_tier: PlanTier
    return_url: str = ""
    cancel_url: str = ""


@router.get("/plans")
async def get_plans():
    """Return all subscription plans with pricing in ZAR."""
    return {
        "plans": [
            {
                "tier": p["id"],
                "name": p["name"],
                "price_zar": p["price_zar"],
                "price_usd": round(p["price_zar"] / 18.5, 2),  # Approximate ZAR→USD
                "projects_per_month": p["projects_per_month"],
                "features": p["features"],
            }
            for p in PLANS.values()
        ],
        "currency": "ZAR",
        "banking_details": {
            "bank": BUSINESS_BANKING["bank_name"],
            "account_name": BUSINESS_BANKING["account_name"],
            "account_number": BUSINESS_BANKING["account_number"],
            "branch_code": BUSINESS_BANKING["branch_code"],
            "swift": BUSINESS_BANKING["swift_code"],
        },
    }


@router.post("/subscribe")
async def subscribe(
    data: SubscribeRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a PayFast subscription or generate EFT payment details."""
    plan = PLANS.get(data.plan_tier)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan tier")

    if data.plan_tier == "free":
        # Free plan — no payment needed
        stmt = select(UserProfile).where(UserProfile.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.plan_tier = PlanTier.free
        await db.commit()
        return {"status": "active", "plan": "free", "detail": "Free plan activated"}

    # Create internal subscription reference
    subscription_id = str(uuid4())

    # Create a pending subscription record
    sub = Subscription(
        id=subscription_id,
        user_id=user_id,
        plan=data.plan_tier,
        status="pending",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
    )
    db.add(sub)
    await db.commit()

    # Generate PayFast subscription URL for card/EFT payments
    if plan["price_zar"] > 0:
        stmt = select(UserProfile).where(UserProfile.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        user_email = user.email if user else ""
        user_name = user.full_name if user else ""

        checkout_url = create_subscription_url(
            plan_tier=data.plan_tier,
            user_email=user_email,
            user_name=user_name,
            return_url=data.return_url or f"{os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:3000')}/dashboard",
            cancel_url=data.cancel_url or f"{os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:3000')}/billing",
            subscription_id=subscription_id,
        )

        return {
            "status": "pending",
            "plan": data.plan_tier,
            "subscription_id": subscription_id,
            "checkout_url": checkout_url,
            "amount_zar": plan["price_zar"],
            "banking_details": {
                "bank": BUSINESS_BANKING["bank_name"],
                "account_name": BUSINESS_BANKING["account_name"],
                "account_number": BUSINESS_BANKING["account_number"],
                "reference": f"SUB-{subscription_id[:8]}",
            },
            "detail": "Pay via PayFast (card/EFT) or direct bank transfer using banking details above.",
        }

    return {"status": "pending", "plan": data.plan_tier, "subscription_id": subscription_id}


@router.get("/subscriptions")
async def get_subscriptions(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all subscriptions for the current user."""
    stmt = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
    result = await db.execute(stmt)
    subs = result.scalars().all()
    return {
        "subscriptions": [
            {
                "id": s.id,
                "plan": s.plan,
                "status": s.status,
                "current_period_start": s.current_period_start.isoformat() if s.current_period_start else None,
                "current_period_end": s.current_period_end.isoformat() if s.current_period_end else None,
                "cancel_at_period_end": s.cancel_at_period_end,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subs
        ]
    }


@router.post("/webhook")
async def payfast_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    PayFast IPN (Instant Payment Notification) webhook endpoint.
    Called by PayFast after payment/subscription events.
    """
    form_data = await request.form()
    data = dict(form_data)

    # Validate the IPN
    if not validate_ipn(data):
        raise HTTPException(status_code=400, detail="Invalid IPN signature")

    payment_status = data.get("payment_status", "")
    m_payment_id = data.get("m_payment_id", "")  # Our subscription_id
    pf_payment_id = data.get("pf_payment_id", "")

    if payment_status == "COMPLETE":
        # Activate the subscription
        stmt = select(Subscription).where(Subscription.id == m_payment_id)
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()

        if sub:
            sub.status = "active"
            sub.payfast_subscription_id = pf_payment_id
            sub.current_period_start = datetime.utcnow()
            sub.current_period_end = datetime.utcnow() + timedelta(days=30)

            # Update user's plan tier
            user_stmt = select(UserProfile).where(UserProfile.id == sub.user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            if user:
                user.plan_tier = PlanTier(sub.plan) if sub.plan in [t.value for t in PlanTier] else PlanTier.free

            await db.commit()

    elif payment_status == "CANCELLED":
        stmt = select(Subscription).where(Subscription.id == m_payment_id)
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "cancelled"
            sub.cancel_at_period_end = True
            await db.commit()

    return {"status": "received"}


@router.post("/invoice")
async def create_invoice(
    plan_tier: PlanTier,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a PDF invoice for EFT payments."""
    plan = PLANS.get(plan_tier)
    if not plan or plan["price_zar"] <= 0:
        raise HTTPException(status_code=400, detail="Invalid plan or free tier")

    stmt = select(UserProfile).where(UserProfile.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    invoice_number = f"PF-{datetime.utcnow().strftime('%Y%m')}-{uuid4().hex[:6].upper()}"
    due_date = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")

    html = generate_invoice_html(
        invoice_number=invoice_number,
        customer_name=user.full_name or "Valued Customer",
        customer_email=user.email,
        plan_tier=plan_tier,
        amount_zar=plan["price_zar"],
        due_date=due_date,
    )

    return {
        "invoice_number": invoice_number,
        "html": html,
        "amount_zar": plan["price_zar"],
        "due_date": due_date,
        "banking": {
            "bank": BUSINESS_BANKING["bank_name"],
            "account_name": BUSINESS_BANKING["account_name"],
            "account_number": BUSINESS_BANKING["account_number"],
            "reference": f"INV-{invoice_number}",
        },
    }