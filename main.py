
bl_info = {
    "name": "Converter for Synty Sourcefiles",
    "author": "Joe",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Asset Tools",
    "description": "Converts sourcefiles from Synty Studios to GLB.",
    "category": "Import-Export",
}

# Global to store complex materials info
flagged_complex_materials = []

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel, PropertyGroup
import os


# ------------------------- Globals

generated_material_counter = 1  # Global or passed-in tracker
bpy.ops.asset.process_synty_sourcefiles()


# ------------------------- Import FBX
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Also delete all unused data blocks (materials, meshes, etc.)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def import_fbx(filepath):
    bpy.ops.import_scene.fbx(filepath=filepath)

def has_image_texture(material):
    if not material or not material.use_nodes:
        return False

    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image is not None:
            return True
    return False


# ------------------------- Material functions

def create_new_generated_material():
    global generated_material_counter
    name = f"Generated_Material_{generated_material_counter:03d}"
    generated_material_counter += 1

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()  # Clean slate
    return mat

def add_bsdf_node_with_inheritance(material, original_material):
    nodes = material.node_tree.nodes
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)

    # Set default values
    base_color = (0.8, 0.8, 0.8, 1.0)
    roughness = 0.5
    metallic = 0.0
    alpha = 1.0

    if original_material and original_material.use_nodes:
        for node in original_material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                base_color = node.inputs["Base Color"].default_value[:]
                roughness = node.inputs["Roughness"].default_value
                metallic = node.inputs["Metallic"].default_value
                # ✅ Pull Alpha from actual Alpha input
                alpha = node.inputs["Alpha"].default_value
                break

    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha

    # Optional: ensure material is set up for transparency
    material.blend_method = 'BLEND'
    material.shadow_method = 'HASHED'
    material.use_backface_culling = False 

    return bsdf

def add_texture_node(material, bsdf_node, texture_path):
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    tex_image = nodes.new("ShaderNodeTexImage")
    tex_image.image = bpy.data.images.load(texture_path, check_existing=True)
    tex_image.location = (-300, 0)

    links.new(tex_image.outputs["Color"], bsdf_node.inputs["Base Color"])

    return tex_image  # <-- RETURN IT!

def add_emission_layer(material, bsdf_node, texture_node=None, strength=1.0, factor=0.25):
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = strength
    emission.location = (200, -200)

    mix = nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = factor
    mix.location = (400, 0)

    # If we have a texture, connect it to Emission color too
    if texture_node:
        links.new(texture_node.outputs["Color"], emission.inputs["Color"])
    else:
        # Use BSDF base color input as fallback
        emission.inputs["Color"].default_value = bsdf_node.inputs["Base Color"].default_value

    links.new(bsdf_node.outputs["BSDF"], mix.inputs[1])
    links.new(emission.outputs["Emission"], mix.inputs[2])

    return mix



def add_output_node(material, shader_output):
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)

    links.new(shader_output.outputs[0], output.inputs["Surface"])

def create_error_material(name="ERROR_MATERIAL"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'OPAQUE'
    mat.shadow_method = 'NONE'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    checker = nodes.new("ShaderNodeTexChecker")
    checker.inputs['Scale'].default_value = 15.0

    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 5.0  # Brighter

    output = nodes.new("ShaderNodeOutputMaterial")

    links.new(checker.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])

    return mat



# ------------------------- Material Operations

def assign_new_generated_material(obj, texture_path, use_emission=True):
    original_material = obj.active_material if obj.active_material else None

    new_mat = create_new_generated_material()
    bsdf = add_bsdf_node_with_inheritance(new_mat, original_material)

    texture_node = None
    if original_material and has_image_texture(original_material):
        texture_node = add_texture_node(new_mat, bsdf, texture_path)

    shader_output = (
        add_emission_layer(new_mat, bsdf, texture_node)
        if use_emission else bsdf
    )

    add_output_node(new_mat, shader_output)

    obj.data.materials.clear()
    obj.data.materials.append(new_mat)




# ------------------------- File Operations

def create_output_folder(input_folder):
    try:
        base_name = os.path.basename(os.path.normpath(input_folder))
        output_folder = os.path.join(input_folder, base_name)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"[INFO] Created output folder: {output_folder}")
        else:
            print(f"[INFO] Output folder already exists: {output_folder}")

        return output_folder
    except Exception as e:
        print(f"[ERROR] Failed to create output folder: {e}")
        return None
    
def get_fbx_files_in_folder(folder_path):
    try:
        fbx_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".fbx") and os.path.isfile(os.path.join(folder_path, f))
        ]
        print(f"[INFO] Found {len(fbx_files)} FBX file(s) in folder: {folder_path}")
        return fbx_files
    except Exception as e:
        print(f"[ERROR] Failed to list FBX files: {e}")
        return []

# ------------------------- Export

def export_as_glb(original_fbx_path, output_folder):
    try:
        base_name = os.path.splitext(os.path.basename(original_fbx_path))[0]
        output_path = os.path.join(output_folder, base_name + ".glb")

        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            export_apply=True,
            export_materials='EXPORT',
            use_selection=False  # Ensure entire scene is exported
        )

        print(f"[INFO] Exported GLB: {output_path}")
        return output_path
    except Exception as e:
        print(f"[ERROR] Failed to export {original_fbx_path} as GLB: {e}")
        return None


# ------------------------- Blender UI 

class ASSET_OT_ProcessFBX(Operator):
    bl_idname = "asset.process_synty_sourcefiles"
    bl_label = "Process FBX Files"
    bl_description = "Imports FBX files, creates fresh materials, and exports as GLB"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.asset_processor_settings
        input_folder = settings.fbx_folder
        texture_file = settings.texture_file

        if not os.path.isdir(input_folder):
            self.report({'ERROR'}, "Invalid FBX folder")
            return {'CANCELLED'}

        if not os.path.isfile(texture_file):
            self.report({'ERROR'}, "Invalid texture file")
            return {'CANCELLED'}

        output_folder = create_output_folder(input_folder)
        if not output_folder:
            self.report({'ERROR'}, "Failed to create output folder")
            return {'CANCELLED'}

        fbx_files = get_fbx_files_in_folder(input_folder)
        if not fbx_files:
            self.report({'WARNING'}, "No FBX files found")
            return {'CANCELLED'}

        use_emission = True  # Future: make this a toggle in the UI

        for fbx_file in fbx_files:
            print(f"\n[PROCESSING] {fbx_file}")
            clear_scene()
            import_fbx(fbx_file)

            # Assign new generated material to each mesh object
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    assign_new_generated_material(obj, texture_file, use_emission=use_emission)

            export_as_glb(fbx_file, output_folder)

        self.report({'INFO'}, f"Processed {len(fbx_files)} file(s).")
        clear_scene()

        if flagged_complex_materials:
            bpy.ops.asset.debug_summary('INVOKE_DEFAULT')

        return {'FINISHED'}




# Property Group to store settings
class AssetProcessorSettings(PropertyGroup):
    fbx_folder: StringProperty(
        name="FBX Folder",
        description="Folder containing FBX files to process",
        subtype='DIR_PATH'
    )

    texture_file: StringProperty(
        name="Texture Image",
        description="Base color texture to apply to models",
        subtype='FILE_PATH'
    )


# UI Panel
class ASSET_PT_ProcessorPanel(Panel):
    bl_label = "FBX Asset Processor"
    bl_idname = "ASSET_PT_processor_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Asset Tools'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.asset_processor_settings

        layout.prop(settings, "fbx_folder")
        layout.prop(settings, "texture_file")
        layout.operator("asset.process_synty_sourcefiles", text="Process FBX Files")

class ASSET_OT_DebugPrompt(bpy.types.Operator):
    bl_idname = "asset.debug_prompt"
    bl_label = "Complex Material Detected"
    bl_options = {'INTERNAL'}

    message: bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}  # Continue

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=500)  # Wider than default

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for line in self.message.split("\n"):
            col.label(text=line)
        col.separator()
        row = col.row()
        row.operator("asset.debug_continue", text="Continue")
        row.operator("asset.debug_cancel", text="Cancel")

class ASSET_OT_DebugContinue(bpy.types.Operator):
    bl_idname = "asset.debug_continue"
    bl_label = "Continue Processing"

    def execute(self, context):
        print("[INFO] User chose to continue after debug prompt.")
        return {'FINISHED'}

class ASSET_OT_DebugCancel(bpy.types.Operator):
    bl_idname = "asset.debug_cancel"
    bl_label = "Cancel Processing"

    def execute(self, context):
        self.report({'WARNING'}, "Processing cancelled by user from summary popup.")
        return {'CANCELLED'}


# ------------------------- Init

class ASSET_OT_DebugSummary(bpy.types.Operator):
    bl_idname = "asset.debug_summary"
    bl_label = "Complex Materials Found"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        print("[INFO] User chose to continue after debug summary.")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=600)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Some materials in the processed files may be complex:")
        col.separator()
        for name, obj, count in flagged_complex_materials:
            col.label(text=f"Material '{name}' on object '{obj}' has {count} nodes.")
        col.separator()
        row = col.row()
        row.operator("asset.debug_summary_continue", text="Continue")
        row.operator("asset.debug_summary_cancel", text="Cancel")

class ASSET_OT_DebugSummaryContinue(bpy.types.Operator):
    bl_idname = "asset.debug_summary_continue"
    bl_label = "Continue Processing"

    def execute(self, context):
        return {'FINISHED'}

class ASSET_OT_DebugSummaryCancel(bpy.types.Operator):
    bl_idname = "asset.debug_summary_cancel"
    bl_label = "Cancel Processing"

    def execute(self, context):
        print("[INFO] User canceled processing from debug summary.")
        raise SystemExit("Stopped by user from summary popup.")

def register():
    bpy.utils.register_class(AssetProcessorSettings)
    bpy.utils.register_class(ASSET_PT_ProcessorPanel)
    bpy.utils.register_class(ASSET_OT_ProcessFBX)
    bpy.utils.register_class(ASSET_OT_DebugSummary)
    bpy.utils.register_class(ASSET_OT_DebugSummaryContinue)
    bpy.utils.register_class(ASSET_OT_DebugSummaryCancel)  # Add this line
    bpy.utils.register_class(ASSET_OT_DebugPrompt)
    bpy.types.Scene.asset_processor_settings = bpy.props.PointerProperty(type=AssetProcessorSettings)

def unregister():
    bpy.utils.unregister_class(AssetProcessorSettings)
    bpy.utils.unregister_class(ASSET_PT_ProcessorPanel)
    bpy.utils.unregister_class(ASSET_OT_DebugPrompt)
    bpy.utils.unregister_class(ASSET_OT_DebugSummaryCancel)
    bpy.utils.unregister_class(ASSET_OT_DebugSummaryContinue)
    bpy.utils.unregister_class(ASSET_OT_DebugSummary)
    bpy.utils.unregister_class(ASSET_OT_ProcessFBX)  # Add this line
    del bpy.types.Scene.asset_processor_settings



if __name__ == "__main__":
    register()

