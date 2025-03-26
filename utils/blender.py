import bpy
from mathutils import Vector

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
	
def get_object_dimensions(obj):
	"""
	Returns the object dimensions.

	Helper function for the rescaling.
	"""

	local_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
	min_corner = Vector((min(v[i] for v in local_bbox) for i in range(3)))
	max_corner = Vector((max(v[i] for v in local_bbox) for i in range(3)))
	return max_corner - min_corner    