import bpy
from ...utils.logging import logger

def remove_import_clutter():
    """Remove common import clutter objects"""
    clutter_names = [
        'icosphere',
        'root.001',
        'armature.001',
        'light',
        'camera',
        'cube',
        'lamp'
    ]

    removed_count = 0

    for obj in list(bpy.context.scene.objects):
        obj_name_lower = obj.name.lower()

        # Check for exact matches or clutter patterns
        should_remove = False

        for clutter_name in clutter_names:
            if clutter_name in obj_name_lower:
                should_remove = True
                break

        # Remove empty objects with no data
        if obj.type == 'EMPTY' and not obj.children:
            should_remove = True

        if should_remove:
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed_count += 1
                logger.debug(f"Removed clutter object: {obj.name}")
            except Exception as e:
                logger.warning(f"Failed to remove clutter object {obj.name}: {e}")

    if removed_count > 0:
        logger.info(f"Removed {removed_count} clutter objects")

def clean_up_clutter(obj):
    """Legacy function for backward compatibility"""
    name = obj.name.lower()
    if name.startswith("iconosphere") or name.startswith("root.001"):
        logger.debug(f"Removing clutter: {obj.name}")
        bpy.data.objects.remove(obj, do_unlink=True)