import bpy
import os
from .state import flagged_complex_materials, generated_material_counter
from .blender_utils import get_object_dimensions
from .fbx_utils import clean_up_clutter, normalize_object_scale, rotate_armatures, normalize_object_scale
import math

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

def import_fbx(filepath):
	"""
	Imports an FBX file into the current Blender scene.

	Uses Blender's built-in FBX importer to load the specified file.
	Applies optional rotation fix and cleans up common import clutter.
	"""

	force_rotate = getattr(bpy.context.scene.asset_processor_settings, "character_rotate_fix", False)
	auto_normalize_scale = getattr(bpy.context.scene.asset_processor_settings, "auto_normalize_scale", False)

	scale_flags = set()

	# Import FBX
	bpy.ops.import_scene.fbx(filepath=filepath)

	# Operations on objects
	for obj in list(bpy.context.scene.objects):
		# Clean up common FBX clutter
		clean_up_clutter(obj)
		# Optional: Attempt to rotate armature (characers)
		if force_rotate:
			rotate_armatures(obj)
		# Optional: Attempt to normalize scale
		if auto_normalize_scale:
			normalize_object_scale(obj)

	bpy.context.scene['scale_flags'] = list(scale_flags)  # Store for export function

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
	
	
def export_as_glb(original_fbx_path, output_folder):
	try:
		base_name = os.path.splitext(os.path.basename(original_fbx_path))[0]

		scale_flags = bpy.context.scene.get('scale_flags', [])
		if scale_flags:
			suffix = "_scaled"
			if "upscaled" in scale_flags and "downscaled" not in scale_flags:
				suffix = "_upscaled"
			elif "downscaled" in scale_flags and "upscaled" not in scale_flags:
				suffix = "_downscaled"
			base_name += suffix

		output_path = os.path.join(output_folder, base_name + ".glb")

		bpy.ops.export_scene.gltf(
			filepath=output_path,
			export_format='GLB',
			export_apply=True,
			export_materials='EXPORT',
			use_selection=False
		)

		print(f"[INFO] Exported GLB: {output_path}")
		return output_path

	except Exception as e:
		print(f"[ERROR] Failed to export {original_fbx_path} as GLB: {e}")
		return None
