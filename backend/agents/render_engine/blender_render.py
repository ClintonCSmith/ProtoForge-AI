import bpy
import sys
import os

def render_model(gltf_path, output_dir, color_rgb=(0.1, 0.1, 0.1)):
    # Clear existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import GLTF
    bpy.ops.import_scene.gltf(filepath=gltf_path)
    
    # Set up world lighting
    world = bpy.data.worlds.new("StudioWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.05, 0.05, 0.08, 1) # Dark navy
    bg.inputs[1].default_value = 1.0

    # Add studio lights
    light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    light_data.energy = 1000
    light_data.size = 5
    light_obj = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (5, 5, 10)
    
    # Add Camera
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Render settings
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    
    angles = {
        "front_iso": (7, -7, 5, 1.1, 0, 0.785),
        "rear_iso": (-7, 7, 5, 1.1, 0, 3.92),
        "top": (0, 0, 10, 0, 0, 0),
        "left": (-10, 0, 2, 1.57, 0, -1.57),
        "right": (10, 0, 2, 1.57, 0, 1.57)
    }
    
    results = {}
    for name, (x, y, z, rx, ry, rz) in angles.items():
        cam_obj.location = (x, y, z)
        cam_obj.rotation_euler = (rx, ry, rz)
        
        output_path = os.path.join(output_dir, f"render_{name}.png")
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        results[name] = output_path
        
    return results

if __name__ == "__main__":
    # Usage: blender --background --python blender_script.py -- <gltf_path> <output_dir> <color_hex>
    args = sys.argv[sys.argv.index("--") + 1:]
    gltf_path = args[0]
    output_dir = args[1]
    # hex color logic can be added
    render_model(gltf_path, output_dir)
