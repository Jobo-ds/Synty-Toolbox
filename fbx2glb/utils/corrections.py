# utils/mesh/corrections.py

import bpy
import math
from mathutils import Vector
from ...utils.blender import get_object_dimensions


def rotate_armatures(obj):
	if obj.type != 'ARMATURE':
		return

	print(f"[ROTATE FIX] Rotating armature: {obj.name}")
	obj.rotation_euler = (
		math.radians(90),   # Stand upright
		0,                  # No flip
		0                   # Face forward
	)

	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


def normalize_object_group_scale(root_obj):
	"""Normalize scale of a parent object based on all its mesh children."""
	def collect_children(obj):
		objs = [obj]
		for child in obj.children:
			objs.extend(collect_children(child))
		return objs

	def get_combined_bounds(objects):
		min_corner = Vector((float('inf'), float('inf'), float('inf')))
		max_corner = Vector((float('-inf'), float('-inf'), float('-inf')))

		for obj in objects:
			if obj.type != 'MESH':
				continue
			for corner in [obj.matrix_world @ Vector(c) for c in obj.bound_box]:
				min_corner = Vector(map(min, min_corner, corner))
				max_corner = Vector(map(max, max_corner, corner))

		return max_corner - min_corner

	all_objs = collect_children(root_obj)
	mesh_objs = [o for o in all_objs if o.type == 'MESH']

	if not mesh_objs:
		return None

	dims = get_combined_bounds(mesh_objs)

	if any(d < 0.1 for d in dims):
		root_obj.scale *= 100
		print(f"[UPSCALE GROUP] {root_obj.name} is small ({dims}), scaling ×100")
	elif any(d > 150.0 for d in dims):
		root_obj.scale *= 0.01
		print(f"[DOWNSCALE GROUP] {root_obj.name} is huge ({dims}), scaling ÷100")
	else:
		return None

	bpy.context.view_layer.objects.active = root_obj
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	return "group_normalized"
