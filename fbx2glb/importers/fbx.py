# importers/fbx.py

import bpy
from ..utils.clean_up import clean_up_clutter
from ..utils.corrections import rotate_armatures, normalize_object_group_scale

def is_ascii_fbx(filepath):
	"""
	Detects if an FBX file is in ASCII format.
	Blender only supports binary FBX files.
	"""
	try:
		with open(filepath, 'rb') as f:
			header = f.read(512)
			if b'Kaydara FBX ASCII' in header:
				return True
			if header.strip().startswith(b';'):  # Legacy ASCII FBX signature
				return True
			return False
	except Exception as e:
		print(f"[ERROR] Could not read FBX header: {e}")
		return False


def import_fbx(filepath):
	"""
	Imports an FBX file into the current Blender scene.

	Uses Blender's built-in FBX importer to load the specified file.
	Applies optional rotation fix and cleans up common import clutter.
	"""

	if is_ascii_fbx(filepath):
		raise RuntimeError(
			f"ASCII FBX files are not supported:\n{filepath}\n\n"
			"Use Autodesk FBX Converter to convert it to binary format."
		)

	scene = bpy.context.scene
	settings = scene.fbx2glb_props

	force_rotate = settings.character_rotate_fix
	auto_normalize_scale = settings.auto_normalize_scale

	scale_flags = set()

	# Import FBX
	bpy.ops.import_scene.fbx(filepath=filepath)

	#Apply scale 1.0
	for obj in bpy.context.selected_objects:
		bpy.context.view_layer.objects.active = obj
		try:
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		except RuntimeError:
			print(f"[SKIP] Could not apply transform to {obj.name} ({obj.type})")	

	# Operations on objects
	for obj in list(bpy.context.scene.objects):
		if settings.remove_clutter:
			clean_up_clutter(obj)
		# Optional: Attempt to rotate armature (characers)
		if force_rotate:
			rotate_armatures(obj)
		# Optional: Attempt to normalize scale
		if auto_normalize_scale and obj.parent is None:
			normalize_object_group_scale(obj)

	bpy.context.scene['scale_flags'] = list(scale_flags)  # Store for export function