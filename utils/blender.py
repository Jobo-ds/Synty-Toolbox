import bpy
from mathutils import Vector

def clear_scene():
	"""
	Thoroughly clears all objects and data from the current Blender scene.

	This comprehensive clearing function ensures a clean slate between file imports
	by removing all objects, meshes, materials, textures, and other data blocks.
	"""

	print("[DEBUG] Starting comprehensive scene clear")

	# Clear any active selections first
	bpy.ops.object.select_all(action='DESELECT')

	# Delete all objects in the scene
	for obj in list(bpy.data.objects):
		try:
			bpy.data.objects.remove(obj, do_unlink=True)
		except Exception as e:
			print(f"[WARNING] Could not remove object {obj.name}: {e}")

	# Clear all collections except the default Scene Collection
	for collection in list(bpy.data.collections):
		if collection.name != "Collection":  # Keep default collection
			try:
				bpy.data.collections.remove(collection)
			except Exception as e:
				print(f"[WARNING] Could not remove collection {collection.name}: {e}")

	# Clear mesh data
	for mesh in list(bpy.data.meshes):
		try:
			bpy.data.meshes.remove(mesh)
		except Exception as e:
			print(f"[WARNING] Could not remove mesh {mesh.name}: {e}")

	# Clear material data
	for material in list(bpy.data.materials):
		try:
			bpy.data.materials.remove(material)
		except Exception as e:
			print(f"[WARNING] Could not remove material {material.name}: {e}")

	# Clear armature data
	for armature in list(bpy.data.armatures):
		try:
			bpy.data.armatures.remove(armature)
		except Exception as e:
			print(f"[WARNING] Could not remove armature {armature.name}: {e}")

	# Clear curve data
	for curve in list(bpy.data.curves):
		try:
			bpy.data.curves.remove(curve)
		except Exception as e:
			print(f"[WARNING] Could not remove curve {curve.name}: {e}")

	# Clear action data (animations)
	for action in list(bpy.data.actions):
		try:
			bpy.data.actions.remove(action)
		except Exception as e:
			print(f"[WARNING] Could not remove action {action.name}: {e}")

	# Clear node groups
	for node_group in list(bpy.data.node_groups):
		try:
			bpy.data.node_groups.remove(node_group)
		except Exception as e:
			print(f"[WARNING] Could not remove node group {node_group.name}: {e}")

	# Clear images (textures) - but respect the texture cache
	try:
		from .texture_cache import texture_cache
		# Protect cached images first
		texture_cache.protect_cached_images()

		images_to_remove = []
		for image in bpy.data.images:
			# Skip default images and cached images
			if (image.name not in ['Render Result', 'Viewer Node'] and
				not image.get('_synty_cached', False)):
				images_to_remove.append(image)

		for image in images_to_remove:
			try:
				bpy.data.images.remove(image)
			except Exception as e:
				print(f"[WARNING] Could not remove image {image.name}: {e}")

		print(f"[DEBUG] Cleared {len(images_to_remove)} non-cached images")
	except ImportError:
		# Fallback if texture cache not available
		images_to_remove = []
		for image in bpy.data.images:
			if image.name not in ['Render Result', 'Viewer Node']:
				images_to_remove.append(image)

		for image in images_to_remove:
			try:
				bpy.data.images.remove(image)
			except Exception as e:
				print(f"[WARNING] Could not remove image {image.name}: {e}")

	# Clear any scene-specific data/flags
	scene = bpy.context.scene
	if 'scale_flags' in scene:
		del scene['scale_flags']

	# Final purge of orphaned data blocks
	try:
		# Run purge multiple times to catch dependencies
		for i in range(3):
			bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
	except Exception as e:
		print(f"[WARNING] Error during orphan purge: {e}")

	# Reset the active object and selection
	bpy.context.view_layer.objects.active = None

	print(f"[DEBUG] Scene cleared - Objects: {len(bpy.data.objects)}, Meshes: {len(bpy.data.meshes)}, Materials: {len(bpy.data.materials)}")

def force_clear_scene():
	"""
	Force a complete scene clear, ignoring texture cache.
	Use this when you need a completely clean slate.
	"""

	print("[DEBUG] Force clearing entire scene")

	# Clear everything without texture cache protection
	for obj in list(bpy.data.objects):
		try:
			bpy.data.objects.remove(obj, do_unlink=True)
		except:
			pass

	for data_type in [bpy.data.meshes, bpy.data.materials, bpy.data.armatures,
					  bpy.data.curves, bpy.data.actions, bpy.data.node_groups,
					  bpy.data.images]:
		for item in list(data_type):
			if hasattr(item, 'name') and item.name not in ['Render Result', 'Viewer Node']:
				try:
					data_type.remove(item)
				except:
					pass

	# Multiple purge passes
	for i in range(3):
		try:
			bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
		except:
			pass

	bpy.context.view_layer.objects.active = None
	print("[DEBUG] Force clear completed")

def clear_scene_legacy():
	"""
	Legacy scene clearing function for backward compatibility.
	"""

	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)

	# Also delete all unused data blocks (materials, meshes, etc.)
	bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
	
def get_object_dimensions(obj):
	"""
	Returns the object dimensions.

	Helper function for the rescaling.
	"""

	local_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
	min_corner = Vector((min(v[i] for v in local_bbox) for i in range(3)))
	max_corner = Vector((max(v[i] for v in local_bbox) for i in range(3)))
	return max_corner - min_corner    