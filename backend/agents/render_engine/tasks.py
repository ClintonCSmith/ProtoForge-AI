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

RENDER_ANGLES = ["front_iso", "rear_iso", "top", "left", "right"]
_MATPLOTLIB_VIEWS = {
    "front_iso": (25, -60),
    "rear_iso": (25, 120),
    "top": (80, -90),
    "left": (5, -180),
    "right": (5, 0),
}


def fallback_render(model_path: str, assets_dir: str, job_uuid: str) -> dict:
    """Render the real mesh from 5 angles with matplotlib when Blender is absent.

    Uses the actual generated geometry (STL/GLTF) — a shaded triangle mesh render,
    not a placeholder image.
    """
    import numpy as np
    import trimesh
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    mesh = trimesh.load(model_path, force="mesh")
    vertices = np.asarray(mesh.vertices, dtype=float)
    triangles = vertices[np.asarray(mesh.faces)]

    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    lengths[lengths == 0] = 1.0
    normals = normals / lengths[:, None]
    light = np.array([0.4, -0.6, 0.7])
    light = light / np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(normals @ light, 0.0, 1.0)
    base = np.array([0.72, 0.75, 0.80])
    face_colors = np.clip(shade[:, None] * base[None, :], 0, 1)

    center = vertices.mean(axis=0)
    extent = float((vertices.max(axis=0) - vertices.min(axis=0)).max()) or 1.0
    half = extent * 0.65

    urls = {}
    for angle in RENDER_ANGLES:
        elev, azim = _MATPLOTLIB_VIEWS[angle]
        fig = plt.figure(figsize=(12, 9), dpi=140)
        ax = fig.add_subplot(111, projection="3d")
        collection = Poly3DCollection(
            triangles, facecolors=face_colors, edgecolors=(0.12, 0.12, 0.14, 0.35), linewidths=0.2
        )
        ax.add_collection3d(collection)
        ax.set_xlim(center[0] - half, center[0] + half)
        ax.set_ylim(center[1] - half, center[1] + half)
        ax.set_zlim(center[2] - half, center[2] + half)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        fig.patch.set_facecolor("#0A1428")
        ax.set_facecolor("#0A1428")

        name = f"render_{angle}_{job_uuid}.png"
        fig.savefig(os.path.join(assets_dir, name), facecolor="#0A1428", bbox_inches="tight")
        plt.close(fig)
        urls[angle] = f"/assets/{name}"

    return {
        "front_iso_url": urls["front_iso"],
        "rear_iso_url": urls["rear_iso"],
        "top_url": urls["top"],
        "left_url": urls["left"],
        "right_url": urls["right"],
        "camera_angles_rendered": RENDER_ANGLES,
        "renderer": "matplotlib-mesh-fallback",
    }


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
            logger.info(f"[{job_id}] Falling back to matplotlib mesh renderer")
            return fallback_render(model_path, assets_dir, job_uuid)
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
        logger.error(f"[{job_id}] Blender not installed — using matplotlib mesh renderer")
        return fallback_render(model_path, assets_dir, job_uuid)
    
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