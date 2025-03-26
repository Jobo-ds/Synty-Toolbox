# utils/mesh/corrections.py

import bpy
import math
from ..blender import get_object_dimensions


def normalize_object_scale(obj):
	if obj.type != 'MESH':
		return None  # no change

	dims = get_object_dimensions(obj)
	name_base = obj.name

	if any(d < 0.01 for d in dims):
		print(f"[UPSCALE] {obj.name} is small ({dims}), scaling ×100")
		obj.scale *= 100
		obj.name = name_base + "_upscaled"
		bpy.context.view_layer.objects.active = obj
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		return "upscaled"

	elif any(d > 150.0 for d in dims):
		print(f"[DOWNSCALE] {obj.name} is huge ({dims}), scaling ÷100")
		obj.scale *= 0.01
		obj.name = name_base + "_downscaled"
		bpy.context.view_layer.objects.active = obj
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		return "downscaled"

	return None
		
	
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