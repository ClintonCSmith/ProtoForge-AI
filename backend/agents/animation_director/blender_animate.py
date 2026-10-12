import bpy
import sys
import os

def animate_model(gltf_path, output_dir, duration=2, fps=24):
    # Clear existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import GLTF
    bpy.ops.import_scene.gltf(filepath=gltf_path)
    
    # Get the imported object (should be the first one)
    obj = None
    for o in bpy.data.objects:
        if o.type == 'MESH':
            obj = o
            break
            
    if not obj:
        print("No mesh found in GLTF")
        return None

    # Add Camera
    cam_data = bpy.data.camera.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_obj.location = (7, -7, 5)
    cam_obj.rotation_euler = (1.1, 0, 0.785)

    # Turntable Animation
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = duration * fps
    
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    
    import math
    obj.rotation_euler = (0, 0, 2 * math.pi)
    obj.keyframe_insert(data_path="rotation_euler", frame=bpy.context.scene.frame_end)
    
    # Set linear interpolation
    for fcurve in obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'

    # Render settings
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' # Fast for animation
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 600
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    
    output_path = os.path.join(output_dir, "animation.mp4")
    bpy.context.scene.render.filepath = output_path
    
    bpy.ops.render.render(animation=True)
    
    return output_path

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    gltf_path = args[0]
    output_dir = args[1]
    animate_model(gltf_path, output_dir)
