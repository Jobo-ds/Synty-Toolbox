# utils/mesh/clean_up.py

import bpy

def clean_up_clutter(obj):
	name = obj.name.lower()
	if name.startswith("iconosphere") or name.startswith("root.001"):
		print(f"[CLEANUP] Removing: {obj.name}")
		bpy.data.objects.remove(obj, do_unlink=True)