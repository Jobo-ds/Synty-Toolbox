# importers/fbx.py

import bpy
from ..utils.mesh.clean_up import clean_up_clutter
from ..utils.mesh.corrections import rotate_armatures, normalize_object_scale


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

	#Apply scale 1.0
	for obj in bpy.context.selected_objects:
		bpy.context.view_layer.objects.active = obj
		try:
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		except RuntimeError:
			print(f"[SKIP] Could not apply transform to {obj.name} ({obj.type})")	

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