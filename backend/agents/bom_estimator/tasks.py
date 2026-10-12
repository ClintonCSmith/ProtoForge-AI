"""
BOMEstimatorAgent — Real Bill of Materials with Octopart API pricing.
Fetches real-time component pricing from Octopart, falls back to database defaults.
"""
import json
import logging
import os
import httpx
from backend.agents.core.celery_app import celery_app

logger = logging.getLogger("BOMEstimatorAgent")

OCTOPART_API_KEY = os.getenv("OCTOPART_API_KEY", "")
OCTOPART_BASE = "https://api.octopart.com/v4"

# Default material costs (USD/kg) — updated periodically
MATERIAL_COSTS = {
    "steel": 1.50, "steel_4140": 2.80, "stainless_steel": 3.50,
    "aluminum": 2.80, "aluminum_6061": 3.20, "aluminum_7075": 5.50,
    "titanium": 35.00, "brass": 8.00, "copper": 9.00,
    "carbon_fiber": 45.00, "abs": 2.50, "nylon": 3.00,
    "polycarbonate": 3.50, "acrylic": 2.00,
}

MANUFACTURING_MULTIPLIERS = {
    "cnc": 2.5,
    "injection_molding": 1.8,
    "sheet_metal": 2.0,
    "casting_sand": 3.2,
    "casting_die": 2.5,
    "3dp_fdm": 4.0,
    "3dp_sla": 6.0,
}


def search_octopart(query: str) -> list[dict]:
    """Search Octopart for component pricing."""
    if not OCTOPART_API_KEY:
        return []
    try:
        resp = httpx.post(
            f"{OCTOPART_BASE}/rest/parts/search",
            json={"query": query, "limit": 3},
            headers={"Authorization": f"Token {OCTOPART_API_KEY}"},
            timeout=15,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        parts = []
        for r in results:
            part = r.get("part", {})
            offers = part.get("offers", [])
            min_price = None
            for o in offers:
                prices = o.get("prices", {}).get("USD", [])
                if prices:
                    try:
                        p = float(prices[0][1]) if isinstance(prices[0], list) else float(prices[0])
                        if min_price is None or p < min_price:
                            min_price = p
                    except:
                        pass
            parts.append({
                "mpn": part.get("mpn", query),
                "manufacturer": part.get("manufacturer", {}).get("name", ""),
                "description": part.get("short_description", ""),
                "unit_price_usd": min_price or 0,
                "lead_time_days": offers[0].get("lead_days", 14) if offers else 14,
            })
        return parts
    except Exception as e:
        logger.warning(f"Octopart search failed: {e}")
        return []


@celery_app.task(bind=True, max_retries=2, default_retry_delay=5)
def estimate_bom(self, job_id: str, input_data: dict) -> dict:
    """Generate a real BOM with Octopart pricing + material cost database."""
    spec = input_data.get("spec", {})
    quantity = int(input_data.get("quantity", 100))
    currency = input_data.get("currency", "USD")
    
    ptype = (spec.get("product_type", "") + " " + spec.get("product_name", "")).lower()
    material_key = "aluminum"
    if "steel" in spec.get("material_preference", "").lower():
        material_key = "steel"
    elif "titanium" in spec.get("material_preference", "").lower():
        material_key = "titanium"
    elif "carbon" in spec.get("material_preference", "").lower():
        material_key = "carbon_fiber"
    
    mat_cost = MATERIAL_COSTS.get(material_key, 2.50)
    dims = spec.get("dimensions_mm", {"length": 100, "width": 50, "height": 25})
    vol_mm3 = dims.get("length", 100) * dims.get("width", 50) * dims.get("height", 25)
    vol_cm3 = vol_mm3 / 1000
    estimated_kg = vol_cm3 * 2.7 / 1000  # ~2.7 g/cm³ for aluminum
    
    # Search Octopart for common components
    fasteners = search_octopart("M4 screw stainless steel") if OCTOPART_API_KEY else []
    bearings = search_octopart("ball bearing 608") if OCTOPART_API_KEY else []
    
    # Build BOM items
    bom_items = [
        {
            "part_number": "PF-BODY-001",
            "description": f"Main body — {spec.get('product_name', 'Part')}",
            "material": spec.get("material_preference", "Aluminum"),
            "qty": 1,
            "unit": "each",
            "unit_cost_usd": round(mat_cost * estimated_kg * 100, 2),
            "total_cost_usd": round(mat_cost * estimated_kg * 100, 2),
            "supplier_options": [{"name": "ProtoForge Manufacturing", "lead_time_days": 14}],
        },
        {
            "part_number": "PF-FAST-001",
            "description": "M4 x 12mm Socket Head Cap Screw",
            "material": "Stainless Steel 304",
            "qty": 8,
            "unit": "each",
            "unit_cost_usd": fasteners[0]["unit_price_usd"] if fasteners else 0.15,
            "total_cost_usd": round((fasteners[0]["unit_price_usd"] if fasteners else 0.15) * 8, 2),
            "supplier_options": [{"name": "McMaster-Carr", "url": "https://mcmaster.com", "lead_time_days": 3}],
        },
    ]
    
    # Manufacturing cost
    mat_total = sum(i["total_cost_usd"] for i in bom_items)
    mfg_mult = MANUFACTURING_MULTIPLIERS.get("cnc", 2.5)
    mfg_cost = mat_total * mfg_mult
    
    # Quantity breaks
    if quantity >= 10000:
        qty_discount = 0.35
    elif quantity >= 1000:
        qty_discount = 0.20
    elif quantity >= 100:
        qty_discount = 0.10
    else:
        qty_discount = 0.0
    
    total_material = mat_total * (1 - qty_discount)
    total_manufacturing = mfg_cost * (1 - qty_discount)
    unit_cost = (total_material + total_manufacturing) / quantity if quantity > 0 else 0
    tooling_cost = 5000 if "injection" in ptype or "drone" in ptype else 500
    
    return {
        "bom": bom_items,
        "total_material_cost_usd": round(total_material, 2),
        "estimated_manufacturing_cost_usd": round(total_manufacturing, 2),
        "estimated_unit_cost_usd": round(unit_cost, 2),
        "tooling_cost_estimate_usd": tooling_cost,
        "material": material_key,
        "weight_kg": round(estimated_kg, 4),
        "supplier_count": len(fasteners) + len(bearings),
        "currency": currency,
        "quantity_priced": quantity,
        "quantity_discount_pct": qty_discount * 100,
    }