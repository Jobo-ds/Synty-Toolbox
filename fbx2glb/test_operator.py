import bpy
import os
from bpy.types import Operator

class SSTOOL_OT_TestFBX2GLBOperator(Operator):
    bl_idname = "sstool.test_fbx2glb_converter"
    bl_label = "Test FBX to GLB (Simple)"
    bl_description = "Simple test version of FBX to GLB converter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Simple test version using legacy approach"""
        try:
            print("[TEST] Starting simple FBX to GLB test")

            # Get basic settings
            props = context.scene.fbx2glb_props
            input_folder = props.fbx_folder

            if not input_folder:
                self.report({'ERROR'}, "No input folder specified")
                return {'CANCELLED'}

            print(f"[TEST] Input folder: {input_folder}")

            # Get one FBX file to test
            fbx_files = []
            for filename in os.listdir(input_folder):
                if filename.lower().endswith('.fbx'):
                    fbx_files.append(os.path.join(input_folder, filename))
                    break  # Just take the first one for testing

            if not fbx_files:
                self.report({'ERROR'}, "No FBX files found")
                return {'CANCELLED'}

            fbx_file = fbx_files[0]
            print(f"[TEST] Processing: {fbx_file}")

            # Clear scene using simple method
            print("[TEST] Clearing scene")
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)

            # Import FBX
            print("[TEST] Importing FBX")
            bpy.ops.import_scene.fbx(filepath=fbx_file)

            # Apply materials using legacy method
            print("[TEST] Applying materials")
            from .utils.material_operations import assign_new_generated_material

            # Simple texture detection
            texture_file = ""
            normal_file = ""
            for filename in os.listdir(input_folder):
                if filename.lower().endswith(('.png', '.jpg')):
                    if 'normal' in filename.lower():
                        normal_file = os.path.join(input_folder, filename)
                    elif not texture_file:
                        texture_file = os.path.join(input_folder, filename)

            # Apply to all mesh objects
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    assign_new_generated_material(obj, texture_file, normal_file)

            # Export GLB
            print("[TEST] Exporting GLB")
            base_name = os.path.splitext(os.path.basename(fbx_file))[0]
            output_path = os.path.join(input_folder, base_name + "_test.glb")

            bpy.ops.export_scene.gltf(
                filepath=output_path,
                export_format='GLB',
                export_apply=True,
                export_materials='EXPORT',
                use_selection=False
            )

            print(f"[TEST] Success! Exported: {output_path}")
            self.report({'INFO'}, f"Test successful: {output_path}")
            return {'FINISHED'}

        except Exception as e:
            print(f"[TEST] Error: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Test failed: {e}")
            return {'CANCELLED'}