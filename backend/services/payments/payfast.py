"""
ProtoForge AI — PayFast Payment Gateway Integration
South Africa's leading payment gateway for SaaS subscriptions.
Supports: recurring billing, instant EFT, card payments, IPN webhooks.
"""

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import httpx

# ─── Configuration ───────────────────────────────────────────────────────────

PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID", "")
PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY", "")
PAYFAST_PASSPHRASE = os.getenv("PAYFAST_PASSPHRASE", "")
PAYFAST_SANDBOX = os.getenv("PAYFAST_SANDBOX", "true").lower() == "true"

PAYFAST_BASE_URL = "https://sandbox.payfast.co.za" if PAYFAST_SANDBOX else "https://www.payfast.co.za"
PAYFAST_ENGINE_URL = f"{PAYFAST_BASE_URL}/eng"
PAYFAST_API_URL = f"{PAYFAST_BASE_URL}/api"

# South African banking details for manual EFT payments
BUSINESS_BANKING = {
    "bank_name": "Capitec Bank",
    "account_name": "IIT AETHELGARD PTY LTD",
    "account_number": "1054813795",
    "branch_code": "450105",
    "branch_name": "Relationship Suite",
    "swift_code": "CABLZAJJ",
    "registration_number": "2026/012903/07",
}

FOUNDER_BANKING = {
    "bank_name": "Discovery Bank",
    "account_name": "Clinton Smith",
    "account_number": "14218867776",
    "branch_code": "679000",
    "swift_code": "DISCZAJJXXX",
}

# ─── Subscription Plans ─────────────────────────────────────────────────────

PLANS = {
    "free": {"id": "free", "name": "Free", "price_zar": 0, "projects_per_month": 1, "features": ["Public sharing", "480p renders"]},
    "starter": {"id": "starter", "name": "Starter", "price_zar": 529, "projects_per_month": 10, "features": ["Full export suite", "4K renders"]},
    "professional": {"id": "professional", "name": "Professional", "price_zar": 1799, "projects_per_month": 50, "features": ["FEA simulation", "Priority queue", "Team sharing"]},
    "enterprise": {"id": "enterprise", "name": "Enterprise", "price_zar": 5499, "projects_per_month": -1, "features": ["Unlimited projects", "Private cloud", "SSO", "Custom models", "SLA"]},
}


@dataclass
class PayFastTransaction:
    """A PayFast payment transaction response."""
    pf_payment_id: str
    pf_client_ref: str
    amount_gross: float
    amount_fee: float
    amount_net: float
    payment_status: str  # COMPLETE, PENDING, FAILED
    billing_date: str
    email_address: str
    name_first: str
    name_last: str
    signature: str


# ─── Helpers ─────────────────────────────────────────────────────────────────

def generate_signature(data: dict, passphrase: Optional[str] = None) -> str:
    """Generate a PayFast-compatible MD5 signature."""
    p = passphrase or PAYFAST_PASSPHRASE
    # Sort keys, concatenate key=value pairs
    sorted_items = sorted(data.items())
    sig_string = "&".join(f"{k}={v}" for k, v in sorted_items if v)
    if p:
        sig_string += f"&passphrase={p}"
    return hashlib.md5(sig_string.encode()).hexdigest()


def validate_ipn(data: dict) -> bool:
    """
    Validate a PayFast IPN (Instant Payment Notification).
    Receives POST data from PayFast, validates signature, then
    sends confirmation back to PayFast to verify authenticity.
    """
    # Step 1: Verify signature
    received_sig = data.pop("signature", "")
    expected_sig = generate_signature(data)
    if received_sig != expected_sig:
        return False

    # Step 2: Send confirmation request to PayFast
    data["command"] = "verify"
    try:
        response = httpx.post(
            f"{PAYFAST_ENGINE_URL}/query/validate",
            data=data,
            timeout=30,
        )
        return response.text.strip() == "VALID"
    except Exception:
        return False


def create_subscription_url(
    plan_tier: str,
    user_email: str,
    user_name: str,
    return_url: str,
    cancel_url: str,
    subscription_id: str,
) -> str:
    """
    Generate a PayFast subscription URL for recurring billing.
    """
    plan = PLANS.get(plan_tier)
    if not plan or plan["price_zar"] <= 0:
        return ""

    data = {
        # Merchant details
        "merchant_id": PAYFAST_MERCHANT_ID,
        "merchant_key": PAYFAST_MERCHANT_KEY,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": f"{os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:8000')}/billing/webhook",

        # Transaction details
        "m_payment_id": subscription_id,  # Our internal reference
        "amount": f"{plan['price_zar']:.2f}",
        "item_name": f"ProtoForge AI — {plan['name']}",
        "item_description": f"{plan['name']} plan: {plan['projects_per_month']} projects/month",

        # Subscriber details
        "email_address": user_email,
        "name_first": user_name.split(" ")[0] if user_name else "",
        "name_last": " ".join(user_name.split(" ")[1:]) if user_name and len(user_name.split(" ")) > 1 else "",

        # Subscription
        "subscription_type": "1",  # Recurring
        "billing_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "recurring_amount": f"{plan['price_zar']:.2f}",
        "frequency": "3",  # Monthly
        "cycles": "0",     # Infinite until cancelled
    }

    data["signature"] = generate_signature(data)
    params = urlencode(data)
    return f"{PAYFAST_ENG_URL}/subscriptions?{params}"


def create_once_off_payment_url(
    user_email: str,
    user_name: str,
    amount_zar: float,
    item_name: str,
    return_url: str,
    cancel_url: str,
    payment_id: str,
) -> str:
    """Generate a one-off PayFast payment URL."""
    data = {
        "merchant_id": PAYFAST_MERCHANT_ID,
        "merchant_key": PAYFAST_MERCHANT_KEY,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": f"{os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:3000')}/api/payments/webhook",
        "m_payment_id": payment_id,
        "amount": f"{amount_zar:.2f}",
        "item_name": item_name,
        "email_address": user_email,
        "name_first": user_name.split(" ")[0] if user_name else "",
        "name_last": " ".join(user_name.split(" ")[1:]) if user_name and len(user_name.split(" ")) > 1 else "",
    }
    data["signature"] = generate_signature(data)
    params = urlencode(data)
    return f"{PAYFAST_ENG_URL}/process?{params}"


def generate_invoice_html(
    invoice_number: str,
    customer_name: str,
    customer_email: str,
    plan_tier: str,
    amount_zar: float,
    due_date: str,
) -> str:
    """Generate an HTML invoice with EFT payment details for manual bank transfer."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Invoice {invoice_number}</title></head>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
<div style="border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 20px;">
    <h1 style="color: #2563eb; margin: 0;">ProtoForge AI</h1>
    <p style="color: #666; margin: 5px 0 0;">Invoice #{invoice_number}</p>
</div>

<div style="margin-bottom: 30px;">
    <h2>Invoice To:</h2>
    <p><strong>{customer_name}</strong><br>{customer_email}</p>
</div>

<table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
    <thead>
        <tr style="background: #2563eb; color: white;">
            <th style="padding: 10px; text-align: left;">Description</th>
            <th style="padding: 10px; text-align: right;">Amount (ZAR)</th>
        </tr>
    </thead>
    <tbody>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">ProtoForge AI — {plan_tier} Plan</td>
            <td style="padding: 10px; text-align: right;">R {amount_zar:.2f}</td>
        </tr>
    </tbody>
    <tfoot>
        <tr>
            <td style="padding: 10px; font-weight: bold; text-align: right;">Total Due:</td>
            <td style="padding: 10px; font-weight: bold; text-align: right; color: #2563eb;">R {amount_zar:.2f}</td>
        </tr>
    </tfoot>
</table>

<div style="background: #f8f9fa; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
    <h3 style="margin-top: 0;">Bank Transfer Details</h3>
    <table style="width: 100%;">
        <tr><td><strong>Bank:</strong></td><td>{BUSINESS_BANKING['bank_name']}</td></tr>
        <tr><td><strong>Account Holder:</strong></td><td>{BUSINESS_BANKING['account_name']}</td></tr>
        <tr><td><strong>Account Number:</strong></td><td>{BUSINESS_BANKING['account_number']}</td></tr>
        <tr><td><strong>Branch Code:</strong></td><td>{BUSINESS_BANKING['branch_code']}</td></tr>
        <tr><td><strong>SWIFT:</strong></td><td>{BUSINESS_BANKING['swift_code']}</td></tr>
        <tr><td><strong>Reference:</strong></td><td><strong>INV-{invoice_number}</strong></td></tr>
    </table>
    <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
        Please use the invoice number as payment reference. Payments are processed within 1-2 business days.
    </p>
</div>

<div style="color: #666; font-size: 0.9em; border-top: 1px solid #ddd; padding-top: 20px;">
    <p><strong>IIT AETHELGARD PTY LTD</strong><br>
    Registration: {BUSINESS_BANKING['registration_number']}<br>
    <strong>Due Date:</strong> {due_date}</p>
</div>
</body>
</html>"""


def verify_plan_access(plan_tier: str, projects_this_month: int) -> dict:
    """
    Verify a user has access based on their plan tier and usage.
    Returns {"allowed": bool, "reason": str}.
    """
    plan = PLANS.get(plan_tier)
    if not plan:
        return {"allowed": False, "reason": "Invalid plan tier"}

    if plan["projects_per_month"] == -1:
        return {"allowed": True, "reason": "Enterprise — unlimited"}

    if projects_this_month >= plan["projects_per_month"]:
        return {
            "allowed": False,
            "reason": f"Plan limit reached: {projects_this_month}/{plan['projects_per_month']} projects this month. Upgrade to continue.",
        }

    return {"allowed": True, "reason": ""}