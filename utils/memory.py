import bpy

def purge_unused_data():
	"""
	Removes all unused datablocks from memory to reduce memory pressure during batch processing.
	Call this after clearing the scene.
	"""
	types_to_clean = [
		bpy.data.meshes,
		bpy.data.materials,
		bpy.data.images,
		bpy.data.textures,
		bpy.data.armatures,
		bpy.data.curves,
	]

	count = 0
	for data_block in types_to_clean:
		for item in list(data_block):
			if item.users == 0:
				data_block.remove(item)
				count += 1

	import gc
	gc.collect()

	print(f"[CLEANUP] Purged {count} unused datablocks.")
