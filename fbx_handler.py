import bpy
import os
from .state import flagged_complex_materials, generated_material_counter

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