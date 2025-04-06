import bpy
import os
from bpy.types import Operator

# -- Custom Utility: Scene Clearing --

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Delete all unused datablocks manually
    data_blocks = (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.textures,
        bpy.data.armatures,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.collections,
    )

    for datablock_list in data_blocks:
        for datablock in datablock_list:
            if datablock.users == 0:
                datablock_list.remove(datablock)

    print("[CLEANUP] Scene cleared and unused datablocks removed.")

# -- Material Merge Logic --

def images_are_equal(img1, img2):
    if img1 is None or img2 is None:
        return img1 == img2
    # For embedded images, compare name and resolution
    return (
        img1.size == img2.size and
        img1.source == img2.source and
        img1.name.split(".")[0] == img2.name.split(".")[0]
    )

def materials_are_duplicates(mat1, mat2):
    if mat1.use_nodes != mat2.use_nodes:
        print(f"❌ [{mat1.name} vs {mat2.name}] Node usage mismatch")
        return False

    if not mat1.use_nodes:
        result = mat1.diffuse_color == mat2.diffuse_color
        if not result:
            print(f"❌ Diffuse color mismatch: {mat1.diffuse_color} vs {mat2.diffuse_color}")
        return result

    def get_principled_bsdf(mat):
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                return node
        return None

    bsdf1 = get_principled_bsdf(mat1)
    bsdf2 = get_principled_bsdf(mat2)

    if not bsdf1 or not bsdf2:
        print(f"❌ Missing Principled BSDF in {mat1.name} or {mat2.name}")
        return False

    # Compare BSDF values: Base Color, Roughness, Metallic, Alpha
    keys = ["Base Color", "Roughness", "Metallic", "Alpha"]
    for key in keys:
        input1 = bsdf1.inputs.get(key)
        input2 = bsdf2.inputs.get(key)
        if input1 and input2 and not input1.is_linked and not input2.is_linked:
            val1 = input1.default_value
            val2 = input2.default_value
            if isinstance(val1, (float, int)):
                if abs(val1 - val2) > 1e-5:
                    print(f"❌ {mat1.name} vs {mat2.name}: {key} mismatch: {val1} vs {val2}")
                    return False
            elif isinstance(val1, (list, tuple)):
                if any(abs(a - b) > 1e-5 for a, b in zip(val1, val2)):
                    print(f"❌ {mat1.name} vs {mat2.name}: {key} mismatch: {val1} vs {val2}")
                    return False

    # Compare Base Color texture image (if linked)
    def get_texture_name(bsdf_input):
        if bsdf_input.is_linked:
            from_node = bsdf_input.links[0].from_node
            if from_node.type == 'TEX_IMAGE' and from_node.image:
                return from_node.image.name.split('.')[0]
        return None

    tex1 = get_texture_name(bsdf1.inputs["Base Color"])
    tex2 = get_texture_name(bsdf2.inputs["Base Color"])
    if tex1 != tex2:
        print(f"❌ {mat1.name} vs {mat2.name}: Base Color texture mismatch: {tex1} vs {tex2}")
        return False

    # Compare Normal Map images (if connected)
    def get_normal_map_image(bsdf_input):
        if not bsdf_input.is_linked:
            return None
        from_node = bsdf_input.links[0].from_node
        if from_node.type == 'NORMAL_MAP' and from_node.inputs["Color"].is_linked:
            tex_node = from_node.inputs["Color"].links[0].from_node
            if tex_node.type == 'TEX_IMAGE' and tex_node.image:
                return tex_node.image.name.split('.')[0]
        return None

    norm1 = get_normal_map_image(bsdf1.inputs["Normal"])
    norm2 = get_normal_map_image(bsdf2.inputs["Normal"])
    if norm1 != norm2:
        print(f"❌ {mat1.name} vs {mat2.name}: Normal Map mismatch: {norm1} vs {norm2}")
        return False

    return True


def merge_duplicate_materials():
    materials = bpy.data.materials
    unique = []
    # Updated replacement mapping
    replacements = {}

    for mat in materials:
        for ref in unique:
            if materials_are_duplicates(mat, ref):
                print(f"[MERGE] Merging {mat.name} into {ref.name}")
                replacements[mat] = ref
                break
        else:
            print(f"[KEEP] Keeping {mat.name}")
            unique.append(mat)

    # Swap material slots using object reference, not name
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for i, slot in enumerate(obj.material_slots):
                if slot.material in replacements:
                    obj.material_slots[i].material = replacements[slot.material]


# -- File Processor --

def process_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    clear_scene()

    if ext == '.blend':
        bpy.ops.wm.open_mainfile(filepath=filepath)

    elif ext == '.glb':
        bpy.ops.import_scene.gltf(filepath=filepath)

    else:
        return

    merge_duplicate_materials()

    if ext == '.blend':
        bpy.ops.wm.save_mainfile(filepath=filepath)

    elif ext == '.glb':
        bpy.ops.object.select_all(action='DESELECT')
        mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']

        for obj in mesh_objs:
            obj.select_set(True)

        if mesh_objs:
            # Ensure the active object is set
            bpy.context.view_layer.objects.active = mesh_objs[0]
            if bpy.context.active_object is not None:
                bpy.ops.export_scene.gltf(
                    filepath=filepath,
                    export_format='GLB',
                    export_apply=True,
                    export_materials='EXPORT',
                    use_selection=False
                )
            else:
                print(f"[SKIP EXPORT] No active object found in {filepath}")
        else:
            print(f"[SKIP EXPORT] No mesh found in {filepath}")

    clear_scene()

# -- Blender Operator --

class SSTOOL_OT_SimplifyMatOperator(Operator):
    bl_idname = "sstool.simplify_materials"
    bl_label = "Simplify Duplicate Materials"
    bl_description = "Merge duplicate materials in all .blend and .glb files in a folder"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        folder = context.scene.simplifymat_props.simplifymat_dir
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(('.blend', '.glb')):
                    try:
                        process_file(os.path.join(root, file))
                        self.report({'INFO'}, f"Processed: {file}")
                    except Exception as e:
                        self.report({'WARNING'}, f"{file} failed: {e}")
                    finally:
                        clear_scene()
        
        return {'FINISHED'}
