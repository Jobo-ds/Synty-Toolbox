#!/usr/bin/env python3
"""
Direct test of the operator logic without imports
"""

import bpy
import os

def clear_scene():
    """Simple scene clearing function"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def process_blend_file_logic(filepath, apply_location=False, apply_rotation=False, apply_scale=False):
    """Direct copy of our operator logic"""
    print(f"[APPLY_MODS] Processing: {filepath}")

    # Clear scene first
    clear_scene()

    # Open the blend file
    bpy.ops.wm.open_mainfile(filepath=filepath)

    # Get all mesh objects
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    if not mesh_objects:
        print(f"[APPLY_MODS] No mesh objects found in {filepath}")
        return False

    print(f"Found {len(mesh_objects)} mesh objects")
    for obj in mesh_objects:
        print(f"  - {obj.name}: rotation = {obj.rotation_euler}")

    # Select all mesh objects for applying transformations
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mesh_objects:
        obj.select_set(True)

    # Set active object
    if mesh_objects:
        bpy.context.view_layer.objects.active = mesh_objects[0]

    print(f"Selected objects: {[obj.name for obj in bpy.context.selected_objects]}")
    print(f"Active object: {bpy.context.active_object.name if bpy.context.active_object else 'None'}")

    # Apply transformations based on user selection
    transformations_applied = []

    if apply_location:
        try:
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
            transformations_applied.append("location")
            print(f"[APPLY_MODS] Applied location transformation")
        except Exception as e:
            print(f"[ERROR] Failed to apply location: {e}")

    if apply_rotation:
        try:
            print(f"[DEBUG] About to apply rotation...")
            result = bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            print(f"[DEBUG] Apply rotation result: {result}")
            transformations_applied.append("rotation")
            print(f"[APPLY_MODS] Applied rotation transformation")
        except Exception as e:
            print(f"[ERROR] Failed to apply rotation: {e}")

    if apply_scale:
        try:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            transformations_applied.append("scale")
            print(f"[APPLY_MODS] Applied scale transformation")
        except Exception as e:
            print(f"[ERROR] Failed to apply scale: {e}")

    print(f"[APPLY_MODS] Applied transformations: {', '.join(transformations_applied)}")

    # Check the result
    for obj in mesh_objects:
        print(f"After apply - {obj.name}: rotation = {obj.rotation_euler}")

    # Save the file
    bpy.ops.wm.save_mainfile(filepath=filepath)
    print(f"[APPLY_MODS] Saved: {filepath}")

    return True

def main():
    """Test the operator logic directly"""
    print("=== Direct Operator Logic Test ===")

    # Create test file
    clear_scene()
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.name = "TestCube"
    cube.rotation_euler = (0.5, 1.0, 1.5)

    test_file = os.path.join(os.path.dirname(__file__), "test_direct.blend")
    bpy.ops.wm.save_as_mainfile(filepath=test_file)

    print(f"Created test file with rotation: {cube.rotation_euler}")

    # Test our operator logic
    success = process_blend_file_logic(test_file, apply_rotation=True)

    # Verify result
    bpy.ops.wm.open_mainfile(filepath=test_file)
    cube = bpy.data.objects.get("TestCube")

    if cube:
        rotation_magnitude = sum(abs(r) for r in cube.rotation_euler)
        print(f"Final rotation: {cube.rotation_euler}")
        print(f"Rotation magnitude: {rotation_magnitude}")

        if rotation_magnitude < 0.001:
            print("SUCCESS: Rotation was applied!")
        else:
            print("FAILURE: Rotation was NOT applied!")
    else:
        print("ERROR: TestCube not found!")

    # Clean up
    try:
        os.remove(test_file)
    except:
        pass

if __name__ == "__main__":
    main()