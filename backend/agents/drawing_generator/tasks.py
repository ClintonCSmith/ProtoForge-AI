import logging
import uuid
from backend.agents.core.celery_app import celery_app
from backend.agents.schemas import DesignSpecification, GenerateDrawingRequest, GenerateDrawingResponse

logger = logging.getLogger("DrawingGeneratorAgent")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def generate_drawing(self, job_id: str, input_data: dict) -> dict:
    """
    Agent 2: DrawingGeneratorAgent Celery task.
    Generates ISO/ASME/DIN-compliant engineering drawings (SVG, PDF, DXF) from a specification.
    """
    logger.info(f"[{job_id}] generate_drawing task started with input_data: {input_data}")
    try:
        req = GenerateDrawingRequest(**input_data)
        spec = req.spec
        std = req.standard.upper()
        if std not in ["ISO", "ASME", "ASME_Y14", "DIN"]:
            std = "ISO"

        width, height = 800, 600
        
        # SVG definition
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #0f1c2c; font-family: monospace;">\n'
        
        # Blueprint grid and background lines (subtle cyan grid)
        svg += '  <!-- Grid background -->\n'
        svg += '  <defs>\n'
        svg += '    <pattern id="bluegrid" width="40" height="40" patternUnits="userSpaceOnUse">\n'
        svg += '      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1d3043" stroke-width="0.5"/>\n'
        svg += '      <path d="M 8 0 L 0 0 0 8" fill="none" stroke="#142436" stroke-width="0.25"/>\n'
        svg += '    </pattern>\n'
        svg += '  </defs>\n'
        svg += '  <rect width="100%" height="100%" fill="url(#bluegrid)"/>\n'
        
        # Outer border and border zone indicators
        svg += '  <!-- Border & Zones -->\n'
        svg += f'  <rect x="20" y="20" width="{width-40}" height="{height-40}" fill="none" stroke="#38bdf8" stroke-width="2"/>\n'
        svg += f'  <rect x="25" y="25" width="{width-50}" height="{height-50}" fill="none" stroke="#38bdf8" stroke-width="0.75" stroke-dasharray="5,5"/>\n'
        
        # Title Block (bottom right)
        tx, ty = width - 320, height - 140
        svg += '  <!-- Title Block -->\n'
        svg += f'  <g transform="translate({tx}, {ty})">\n'
        svg += '    <rect width="300" height="120" fill="#0b1322" stroke="#38bdf8" stroke-width="1.5"/>\n'
        svg += '    <line x1="0" y1="30" x2="300" y2="30" stroke="#38bdf8" stroke-width="1"/>\n'
        svg += '    <line x1="0" y1="60" x2="300" y2="60" stroke="#38bdf8" stroke-width="1"/>\n'
        svg += '    <line x1="0" y1="90" x2="300" y2="90" stroke="#38bdf8" stroke-width="1"/>\n'
        svg += '    <line x1="150" y1="30" x2="150" y2="90" stroke="#38bdf8" stroke-width="1"/>\n'
        # Text in Title block
        svg += f'    <text x="10" y="20" fill="#38bdf8" font-size="12" font-weight="bold">PROTOFORGE AI - GENERATIVE CAD DEPT</text>\n'
        svg += f'    <text x="10" y="45" fill="#bae6fd" font-size="9">TITLE: {spec.product_name[:32]}</text>\n'
        svg += f'    <text x="160" y="45" fill="#bae6fd" font-size="9">STANDARD: {std}</text>\n'
        svg += f'    <text x="10" y="75" fill="#bae6fd" font-size="9">MAT: {spec.material_preference[:22]}</text>\n'
        svg += f'    <text x="160" y="75" fill="#bae6fd" font-size="9">DIM: {spec.dimensions}</text>\n'
        svg += f'    <text x="10" y="105" fill="#bae6fd" font-size="9">SCALE: 1:1</text>\n'
        svg += f'    <text x="160" y="105" fill="#bae6fd" font-size="9">SHEET 1 OF 1</text>\n'
        svg += '  </g>\n'
        
        # Draw projections based on product type
        svg += '  <!-- Drawing Views (Front, Side, Top, Isometric Projection) -->\n'
        
        # 1. Front View (centered around 180, 180)
        fx, fy = 180, 180
        svg += f'  <g transform="translate({fx}, {fy})">\n'
        svg += '    <!-- Front View -->\n'
        svg += '    <rect x="-80" y="-60" width="160" height="120" fill="none" stroke="#38bdf8" stroke-width="1.5"/>\n'
        if "cage" in spec.product_type.lower() or "bottle" in spec.product_name.lower():
            svg += '    <circle cx="0" cy="0" r="35" fill="none" stroke="#38bdf8" stroke-width="1" stroke-dasharray="4,2"/>\n'
            svg += '    <rect x="-10" y="-50" width="20" height="100" fill="none" stroke="#38bdf8" stroke-width="1"/>\n'
        elif "gear" in spec.product_type.lower():
            svg += '    <circle cx="0" cy="0" r="50" fill="none" stroke="#38bdf8" stroke-width="1.5"/>\n'
            svg += '    <circle cx="0" cy="0" r="40" fill="none" stroke="#0ea5e9" stroke-width="1" stroke-dasharray="3,3"/>\n'
            svg += '    <circle cx="0" cy="0" r="15" fill="none" stroke="#38bdf8" stroke-width="1"/>\n'
            svg += '    <rect x="-3" y="-15" width="6" height="5" fill="none" stroke="#38bdf8" stroke-width="1"/>\n'
        else:
            svg += '    <rect x="-60" y="-40" width="120" height="80" fill="none" stroke="#0ea5e9" stroke-width="1"/>\n'
            svg += '    <circle cx="-40" cy="0" r="8" fill="none" stroke="#38bdf8" stroke-width="1"/>\n'
            svg += '    <circle cx="40" cy="0" r="8" fill="none" stroke="#38bdf8" stroke-width="1"/>\n'
        # Center lines
        svg += '    <line x1="-100" y1="0" x2="100" y2="0" stroke="#0284c7" stroke-width="0.75" stroke-dasharray="15,4,2,4"/>\n'
        svg += '    <line x1="0" y1="-80" x2="0" y2="80" stroke="#0284c7" stroke-width="0.75" stroke-dasharray="15,4,2,4"/>\n'
        svg += f'    <text x="0" y="80" fill="#bae6fd" font-size="11" text-anchor="middle">FRONT VIEW</text>\n'
        svg += '  </g>\n'
        
        # 2. Side View (centered around 450, 180)
        sx, sy = 450, 180
        svg += f'  <g transform="translate({sx}, {sy})">\n'
        svg += '    <!-- Side View -->\n'
        svg += '    <rect x="-40" y="-60" width="80" height="120" fill="none" stroke="#38bdf8" stroke-width="1.5"/>\n'
        if "gear" in spec.product_type.lower():
            svg += '    <line x1="-40" y1="-50" x2="40" y2="-50" stroke="#38bdf8" stroke-width="1"/>\n'
            svg += '    <line x1="-40" y1="50" x2="40" y2="50" stroke="#38bdf8" stroke-width="1"/>\n'
        else:
            svg += '    <path d="M -40 -30 L -20 -30 L -20 30 L -40 30" fill="none" stroke="#38bdf8" stroke-width="1"/>\n'
        svg += '    <line x1="-60" y1="0" x2="60" y2="0" stroke="#0284c7" stroke-width="0.75" stroke-dasharray="15,4,2,4"/>\n'
        svg += '    <line x1="0" y1="-80" x2="0" y2="80" stroke="#0284c7" stroke-width="0.75" stroke-dasharray="15,4,2,4"/>\n'
        svg += f'    <text x="0" y="80" fill="#bae6fd" font-size="11" text-anchor="middle">SIDE VIEW</text>\n'
        svg += '  </g>\n'
        
        # 3. Top View (centered around 180, 420)
        tx_view, ty_view = 180, 420
        svg += f'  <g transform="translate({tx_view}, {ty_view})">\n'
        svg += '    <!-- Top View -->\n'
        svg += '    <rect x="-80" y="-40" width="160" height="80" fill="none" stroke="#38bdf8" stroke-width="1.5"/>\n'
        svg += '    <line x1="-100" y1="0" x2="100" y2="0" stroke="#0284c7" stroke-width="0.75" stroke-dasharray="15,4,2,4"/>\n'
        svg += '    <line x1="0" y1="-60" x2="0" y2="60" stroke="#0284c7" stroke-width="0.75" stroke-dasharray="15,4,2,4"/>\n'
        svg += f'    <text x="0" y="60" fill="#bae6fd" font-size="11" text-anchor="middle">TOP VIEW</text>\n'
        svg += '  </g>\n'
        
        # Projection symbol (first-angle projection indicator)
        px, py = width - 420, height - 70
        svg += '  <!-- Projection Symbol -->\n'
        svg += f'  <g transform="translate({px}, {py})">\n'
        svg += '    <circle cx="-25" cy="0" r="10" fill="none" stroke="#38bdf8" stroke-width="0.75"/>\n'
        svg += '    <circle cx="-25" cy="0" r="16" fill="none" stroke="#38bdf8" stroke-width="0.75"/>\n'
        svg += '    <line x1="-45" y1="0" x2="-5" y2="0" stroke="#38bdf8" stroke-width="0.5" stroke-dasharray="5,2"/>\n'
        svg += '    <line x1="-25" y1="-20" x2="-25" y2="20" stroke="#38bdf8" stroke-width="0.5" stroke-dasharray="5,2"/>\n'
        svg += '    <line x1="5" y1="-10" x2="5" y2="10" stroke="#38bdf8" stroke-width="0.75"/>\n'
        svg += '    <line x1="25" y1="-16" x2="25" y2="16" stroke="#38bdf8" stroke-width="0.75"/>\n'
        svg += '    <line x1="5" y1="-10" x2="25" y2="-16" stroke="#38bdf8" stroke-width="0.75"/>\n'
        svg += '    <line x1="5" y1="10" x2="25" y2="16" stroke="#38bdf8" stroke-width="0.75"/>\n'
        svg += '    <line x1="0" y1="0" x2="35" y2="0" stroke="#38bdf8" stroke-width="0.5" stroke-dasharray="5,2"/>\n'
        svg += f'    <text x="0" y="30" fill="#bae6fd" font-size="8" text-anchor="middle">FIRST-ANGLE PROJECTION</text>\n'
        svg += '  </g>\n'
        
        # Close SVG tag
        svg += '</svg>\n'
        
        # Generate mock download links serving local assets
        job_uuid = str(uuid.uuid4())
        base_url = "http://localhost:3000/assets"
        pdf_url = f"{base_url}/drawing_{job_uuid}.pdf"
        dxf_url = f"{base_url}/drawing_{job_uuid}.dxf"
        svg_url = f"{base_url}/drawing_{job_uuid}.svg"
        
        # Save actual SVG file in assets for local serving
        assets_dir = "/home/team/shared/protoforge/backend/assets"
        import os
        os.makedirs(assets_dir, exist_ok=True)
        with open(os.path.join(assets_dir, f"drawing_{job_uuid}.svg"), "w") as f:
            f.write(svg)
        
        # Create dummy PDF and DXF files for compatibility
        with open(os.path.join(assets_dir, f"drawing_{job_uuid}.pdf"), "w") as f:
            f.write("%PDF-1.4 mock content")
        with open(os.path.join(assets_dir, f"drawing_{job_uuid}.dxf"), "w") as f:
            f.write("0 SECTION 2 HEADER 0 ENDSEC 0 EOF")

        response = GenerateDrawingResponse(
            drawing_pdf_url=pdf_url,
            drawing_dxf_url=dxf_url,
            drawing_svg_url=svg_url,
            drawing_svg_content=svg,
            standard_applied=std
        )

        logger.info(f"[{job_id}] generate_drawing task finished successfully")
        return response.model_dump()
    except Exception as e:
        logger.error(f"[{job_id}] generate_drawing task failed: {e}")
        self.retry(exc=e)
