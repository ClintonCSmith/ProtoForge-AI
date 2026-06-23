import logging
from agents.core.celery_app import celery_app
from agents.schemas import EstimateBOMRequest, EstimateBOMResponse, BOMItem

logger = logging.getLogger("BOMEstimatorAgent")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def estimate_bom(self, job_id: str, input_data: dict) -> dict:
    """
    Agent 10: BOMEstimatorAgent Celery task.
    Decomposes specification into materials and hardware parts, queries standard unit pricing,
    applies manufacturing multipliers, and returns comprehensive BOM estimates.
    """
    logger.info(f"[{job_id}] estimate_bom task started with input_data: {input_data}")
    try:
        req = EstimateBOMRequest(**input_data)
        qty = req.quantity
        spec = req.spec
        
        # Currency conversion rates
        currency_rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.78,
            "ZAR": 18.40
        }
        rate = currency_rates.get(req.currency.upper(), 1.0)
        
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
        multiplier = 2.5
        if "cage" in spec.product_type.lower() or "molding" in spec.complexity:
             multiplier = 1.8
             tooling = 12000.00  # High initial tooling cost for molding
        else:
             tooling = 0.00
             
        # Volume discount: 10% for 100+, 20% for 1000+
        discount = 1.0
        if qty >= 1000:
            discount = 0.8
        elif qty >= 100:
            discount = 0.9
            
        est_mfg_cost = total_mat * multiplier * discount
        unit_cost = (total_mat + est_mfg_cost) + (tooling / qty)
        
        response = EstimateBOMResponse(
            bom=bom,
            total_material_cost_usd=float(total_mat),
            estimated_manufacturing_cost_usd=float(est_mfg_cost * qty),
            tooling_cost_estimate_usd=float(tooling),
            estimated_unit_cost_usd=float(unit_cost),
            exchange_rate=float(rate),
            currency=req.currency.upper()
        )

        logger.info(f"[{job_id}] estimate_bom task finished successfully")
        return response.model_dump()
    except Exception as e:
        logger.error(f"[{job_id}] estimate_bom task failed: {e}")
        self.retry(exc=e)
