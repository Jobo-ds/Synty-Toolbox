import bpy
import os
from .state import flagged_complex_materials, generated_material_counter

def clear_scene():
	"""
	Clears all objects from the current Blender scene.

	Deletes all objects, then purges unused data blocks like materials and meshes.
	Useful to reset the scene before importing a new FBX.
	"""
		
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)
	
	# Also delete all unused data blocks (materials, meshes, etc.)
	bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def import_fbx(filepath):
	"""
	Imports an FBX file into the current Blender scene.

	Uses Blender's built-in FBX importer to load the specified file.
	Applies optional rotation fix and cleans up common import clutter.
	"""

	force_rotate = getattr(bpy.context.scene.asset_processor_settings, "character_rotate_fix", False)

	# Import FBX
	bpy.ops.import_scene.fbx(filepath=filepath)

	# Debug: print all objects after import
	print("[DEBUG] All objects after FBX import:")
	for obj in bpy.context.scene.objects:
		print(f" - {obj.name} ({obj.type})")

	# Optional rotation fix
	if force_rotate:
		import math
		armature = next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)

		if armature:
			print(f"[ROTATE FIX] Rotating armature: {armature.name}")
			armature.rotation_euler = (
				math.radians(90),   # Stand upright
				0,                  # No flip
				0				   # Turn around to face the camera/front
			)


			bpy.context.view_layer.objects.active = armature
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		else:
			print("[ROTATE FIX] Armature not found — skipping rotation.")

	# Clean up common FBX clutter
	for obj in list(bpy.context.scene.objects):
		name = obj.name.lower()
		if name.startswith("iconosphere") or name.startswith("root.001"):
			print(f"[CLEANUP] Removing: {obj.name}")
			bpy.data.objects.remove(obj, do_unlink=True)	

	# Remove Blender's hidden GLTF helper collection
	gltf_collection = bpy.data.collections.get("glTF_not_exported")
	if gltf_collection:
		bpy.data.collections.remove(gltf_collection)
		print("[CLEANUP] Removed glTF_not_exported collection")




def has_image_texture(material):
	"""
	Checks if a material contains an image texture node.

	Iterates over all nodes in the material's node tree to find a valid image.
	Used to determine whether to reuse texture input or generate a new material.
	"""

	if not material or not material.use_nodes:
		return False

	for node in material.node_tree.nodes:
		if node.type == 'TEX_IMAGE' and node.image is not None:
			return True
	return False

def create_output_folder(input_folder):
	"""
	Creates an output folder inside the input directory.

	Uses the name of the input folder to generate a subdirectory for exported files.
	Returns the path if successful, or None on error.
	"""

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
	"""
	Finds all FBX files in the given folder path.

	Scans the directory for files ending in .fbx (case-insensitive).
	Returns a list of full file paths.
	"""

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
	"""
	Exports the current Blender scene as a GLB file.

	Generates a .glb filename based on the original FBX name and writes it to the output folder.
	Returns the export path if successful, or None on failure.
	"""

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