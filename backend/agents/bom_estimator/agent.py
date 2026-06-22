from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/agents", tags=["BOMEstimatorAgent"])

class DesignSpecification(BaseModel):
    product_name: str
    product_type: str
    dimensions: str
    material_preference: str
    color: str
    complexity: str
    functional_features: List[str]

class BOMItem(BaseModel):
    part_number: str
    description: str
    material: str
    qty: int
    unit: str
    unit_cost_usd: float
    total_cost_usd: float
    supplier_options: List[str]

class EstimateBOMRequest(BaseModel):
    spec: DesignSpecification
    model_gltf_url: str
    quantity: int = Field(1, description="Production volume size")
    currency: str = Field("USD", description="Currency preset: USD, EUR, GBP, or ZAR")

class EstimateBOMResponse(BaseModel):
    bom: List[BOMItem]
    total_material_cost_usd: float
    estimated_manufacturing_cost_usd: float
    tooling_cost_estimate_usd: float
    estimated_unit_cost_usd: float
    exchange_rate: float
    currency: str

@router.post("/bom", response_model=EstimateBOMResponse)
async def estimate_bom(data: EstimateBOMRequest):
    """
    Agent 10: BOMEstimatorAgent endpoint.
    Decomposes specification into materials and hardware parts, queries standard unit pricing,
    applies manufacturing multipliers, and returns comprehensive BOM estimates.
    """
    qty = data.quantity
    spec = data.spec
    
    # Currency conversion rates (mock Open Exchange Rates)
    currency_rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.78,
        "ZAR": 18.40
    }
    rate = currency_rates.get(data.currency.upper(), 1.0)
    
    # Analyze specification and construct components
    bom = []
    
    # Core raw material
    mat_pref = spec.material_preference
    mat_unit_cost = 12.50 # Al6061 base cost
    if "carbon" in mat_pref.lower() or "cfrp" in mat_pref.lower():
        mat_unit_cost = 45.00
    elif "brass" in mat_pref.lower() or "bronze" in mat_pref.lower():
        mat_unit_cost = 25.00
    elif "steel" in mat_pref.lower():
        mat_unit_cost = 8.50
        
    bom.append(BOMItem(
        part_number="PF-RAW-001",
        description=f"Raw stock block ({spec.dimensions})",
        material=mat_pref,
        qty=1,
        unit="pcs",
        unit_cost_usd=mat_unit_cost,
        total_cost_usd=mat_unit_cost,
        supplier_options=["McMaster-Carr", "OnlineMetals", "Alro Steel"]
    ))
    
    # Standard fasteners and brackets depending on features
    for idx, feature in enumerate(spec.functional_features):
        part_no = f"PF-FAST-{idx+1:03d}"
        desc = f"Standard {feature.lower()} fixture/screw"
        bom.append(BOMItem(
            part_number=part_no,
            description=desc,
            material="Stainless Steel A2",
            qty=4,
            unit="pcs",
            unit_cost_usd=0.45,
            total_cost_usd=1.80,
            supplier_options=["Grainger", "Fastenal", "Misumi"]
        ))
        
    # Calculate costs
    total_mat = sum(item.total_cost_usd for item in bom)
    
    # Manufacturing cost multiplier
    # Injection Molding = 1.8x, CNC Machining = 2.5x, 3D printing = 4.0x
    multiplier = 2.5
    if "cage" in spec.product_type.lower() or "molding" in spec.complexity:
         multiplier = 1.8
         tooling = 12000.00  # High initial tooling cost for molding
    else:
         tooling = 0.00
         
    # Volume discount discount: 10% for 100+, 20% for 1000+
    discount = 1.0
    if qty >= 1000:
        discount = 0.8
    elif qty >= 100:
        discount = 0.9
        
    est_mfg_cost = total_mat * multiplier * discount
    unit_cost = (total_mat + est_mfg_cost) + (tooling / qty)
    
    return EstimateBOMResponse(
        bom=bom,
        total_material_cost_usd=float(total_mat),
        estimated_manufacturing_cost_usd=float(est_mfg_cost * qty),
        tooling_cost_estimate_usd=float(tooling),
        estimated_unit_cost_usd=float(unit_cost),
        exchange_rate=float(rate),
        currency=data.currency.upper()
    )

@router.get("/bom/export", response_class=StreamingResponse)
async def export_bom_csv(product_name: str = "product"):
    """
    Downloads the estimated BOM as a standard CSV format sheet.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Part Number", "Description", "Material", "Qty", "Unit", "Unit Cost (USD)", "Total Cost (USD)"])
    writer.writerow(["PF-RAW-001", "Raw stock block", "Aluminum 6061-T6", 1, "pcs", 12.50, 12.50])
    writer.writerow(["PF-FAST-001", "M5 Threaded mounting bolt", "Stainless Steel", 4, "pcs", 0.45, 1.80])
    
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=BOM_{product_name.replace(' ', '_')}.csv"
    return response
