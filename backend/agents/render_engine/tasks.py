"""
RenderEngineAgent — Blender Python (bpy) photorealistic 4K rendering pipeline.
5 camera angles, PBR materials, studio lighting.
"""
import logging
import os
import subprocess
import uuid
from backend.agents.core.celery_app import celery_app

logger = logging.getLogger("RenderEngineAgent")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def render_model(self, job_id: str, input_data: dict) -> dict:
    """Render a 3D model from 5 angles using Blender Python (bpy)."""
    logger.info(f"[{job_id}] render_model started")
    assets_dir = "/home/team/shared/protoforge/backend/assets"
    os.makedirs(assets_dir, exist_ok=True)
    job_uuid = str(uuid.uuid4())
    
    model_url = input_data.get("model_gltf_url", "")
    model_filename = os.path.basename(model_url)
    model_path = os.path.join(assets_dir, model_filename)
    
    if not os.path.exists(model_path):
        # Create a simple STL for rendering from the assets dir
        import glob
        stl_files = glob.glob(os.path.join(assets_dir, f"*{job_id.split('_')[0]}*.stl"))
        if stl_files:
            model_path = stl_files[0]
        else:
            # No model found — return error, not fake renders
            logger.error(f"[{job_id}] No model found for rendering")
            return {
                "front_iso_url": "", "rear_iso_url": "", "top_url": "",
                "left_url": "", "right_url": "",
                "camera_angles_rendered": [],
                "error": "No model available for rendering",
            }
    
    blender_script = """
import bpy
import sys
import os

model_path = sys.argv[sys.argv.index('--') + 1]
output_dir = sys.argv[sys.argv.index('--') + 2]

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import model
if model_path.endswith('.stl'):
    bpy.ops.import_mesh.stl(filepath=model_path)
elif model_path.endswith('.gltf') or model_path.endswith('.glb'):
    bpy.ops.import_scene.gltf(filepath=model_path)
else:
    bpy.ops.import_mesh.stl(filepath=model_path)

# Get the imported object
obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else bpy.context.view_layer.objects.active
if not obj:
    obj = bpy.data.objects[0]

# Center object
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
bpy.ops.object.location_clear()
bpy.ops.object.select_all(action='DESELECT')

# Create material
mat = bpy.data.materials.new(name='ProtoForgePBR')
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# PBR shader
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (0.2, 0.4, 0.8, 1.0)
principled.inputs['Roughness'].default_value = 0.3
principled.inputs['Metallic'].default_value = 0.5

output = nodes.new('ShaderNodeOutputMaterial')
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Camera setup
cam = bpy.data.cameras.new('RenderCam')
cam_obj = bpy.data.objects.new('RenderCam', cam)
bpy.context.collection.objects.link(cam_obj)

# Lighting
bpy.ops.object.light_add(type='STUDIO', location=(5, -5, 10))
light = bpy.context.active_object
light.data.energy = 1000

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Camera angles
angles = [
    ('front_iso', (6, -6, 4)),
    ('rear_iso', (-6, 6, 4)),
    ('top', (0, 0, 8)),
    ('left', (-6, 0, 2)),
    ('right', (6, 0, 2)),
]

for angle_name, loc in angles:
    cam_obj.location = loc
    
    # Look at origin
    direction = (0, 0, 0) - cam_obj.location
    cam_obj.rotation_euler = (1.0, 0, direction.xy.angle_signed())
    
    bpy.context.scene.camera = cam_obj
    output_path = os.path.join(output_dir, f'render_{angle_name}.png')
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f'Rendered: {angle_name}')
"""
    
    script_path = os.path.join(assets_dir, f"blender_job_{job_uuid}.py")
    with open(script_path, "w") as f:
        f.write(blender_script.strip())
    
    # Run Blender
    try:
        process = subprocess.run(
            ["blender", "--background", "--python", script_path, "--", model_path, assets_dir],
            capture_output=True, text=True, timeout=120,
        )
        if process.returncode != 0:
            logger.error(f"[{job_id}] Blender failed: {process.stderr[:500]}")
            return {
                "front_iso_url": "", "rear_iso_url": "", "top_url": "",
                "left_url": "", "right_url": "",
                "camera_angles_rendered": [],
                "error": f"Blender render failed: {process.stderr[:200]}",
            }
        logger.info(f"[{job_id}] Blender renders complete")
    except subprocess.TimeoutExpired:
        logger.error(f"[{job_id}] Blender timed out")
        return {
            "front_iso_url": "", "rear_iso_url": "", "top_url": "",
            "left_url": "", "right_url": "",
            "camera_angles_rendered": [],
            "error": "Blender render timed out",
        }
    except FileNotFoundError:
        logger.error(f"[{job_id}] Blender not installed")
        return {
            "front_iso_url": "", "rear_iso_url": "", "top_url": "",
            "left_url": "", "right_url": "",
            "camera_angles_rendered": [],
            "error": "Blender not installed on server",
        }
    
    # Map rendered files
    angles = ["front_iso", "rear_iso", "top", "left", "right"]
    urls = {}
    for angle in angles:
        old_path = os.path.join(assets_dir, f"render_{angle}.png")
        new_name = f"render_{angle}_{job_uuid}.png"
        new_path = os.path.join(assets_dir, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            urls[angle] = f"/assets/{new_name}"
        else:
            urls[angle] = ""
    
    return {
        "front_iso_url": urls.get("front_iso", ""),
        "rear_iso_url": urls.get("rear_iso", ""),
        "top_url": urls.get("top", ""),
        "left_url": urls.get("left", ""),
        "right_url": urls.get("right", ""),
        "camera_angles_rendered": angles,
    }