#!/usr/bin/env python3
"""
Test script for Apply Modifications functionality
Run with: blender --background --python test_apply_modifications.py
"""

import bpy
import os
import sys
import mathutils

def create_test_blend_file():
    """Create a test blend file with a rotated cube"""

    # Clear default scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Add a cube
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.name = "TestCube"

    # Apply some transformations
    cube.location = (1.0, 2.0, 3.0)
    cube.rotation_euler = (0.5, 1.0, 1.5)  # Some rotation in radians
    cube.scale = (1.5, 2.0, 0.8)

    # Print initial values
    print(f"Initial cube location: {cube.location}")
    print(f"Initial cube rotation: {cube.rotation_euler}")
    print(f"Initial cube scale: {cube.scale}")

    # Save test file
    test_file = os.path.join(os.path.dirname(__file__), "test_rotation.blend")
    bpy.ops.wm.save_as_mainfile(filepath=test_file)
    print(f"Created test file: {test_file}")

    return test_file

def test_apply_rotation(test_file):
    """Test the apply rotation functionality"""

    print("\n=== Testing Apply Rotation ===")

    # Clear scene and load test file
    bpy.ops.wm.open_mainfile(filepath=test_file)

    # Get the cube
    cube = bpy.data.objects.get("TestCube")
    if not cube:
        print("ERROR: TestCube not found!")
        return False

    print(f"Before apply - Location: {cube.location}")
    print(f"Before apply - Rotation: {cube.rotation_euler}")
    print(f"Before apply - Scale: {cube.scale}")

    # Select the cube
    bpy.ops.object.select_all(action='DESELECT')
    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube

    print(f"Selected objects: {[obj.name for obj in bpy.context.selected_objects]}")
    print(f"Active object: {bpy.context.active_object.name if bpy.context.active_object else 'None'}")

    # Try to apply rotation
    try:
        print("Attempting to apply rotation...")
        result = bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        print(f"Apply rotation result: {result}")
    except Exception as e:
        print(f"ERROR applying rotation: {e}")
        return False

    print(f"After apply - Location: {cube.location}")
    print(f"After apply - Rotation: {cube.rotation_euler}")
    print(f"After apply - Scale: {cube.scale}")

    # Check if rotation was actually applied (should be close to 0,0,0)
    rotation_magnitude = sum(abs(r) for r in cube.rotation_euler)
    print(f"Rotation magnitude after apply: {rotation_magnitude}")

    if rotation_magnitude < 0.001:
        print("SUCCESS: Rotation was applied successfully!")
        return True
    else:
        print("FAILURE: Rotation was not applied!")
        return False

def test_our_operator_logic(test_file):
    """Test our specific operator logic"""

    print("\n=== Testing Our Operator Logic ===")

    # Simulate our operator logic
    bpy.ops.wm.open_mainfile(filepath=test_file)

    # Get all mesh objects (like our operator does)
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    print(f"Found mesh objects: {[obj.name for obj in mesh_objects]}")

    if not mesh_objects:
        print("ERROR: No mesh objects found!")
        return False

    cube = mesh_objects[0]
    print(f"Testing with object: {cube.name}")
    print(f"Before - Rotation: {cube.rotation_euler}")

    # Our operator's selection logic
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mesh_objects:
        obj.select_set(True)
        print(f"Selected: {obj.name}")

    # Set active object
    if mesh_objects:
        bpy.context.view_layer.objects.active = mesh_objects[0]
        print(f"Set active object: {bpy.context.active_object.name}")

    # Apply rotation (our operator's logic)
    try:
        print("Applying rotation with our operator logic...")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        print("Apply rotation completed")
    except Exception as e:
        print(f"ERROR in our operator logic: {e}")
        return False

    print(f"After - Rotation: {cube.rotation_euler}")

    # Check result
    rotation_magnitude = sum(abs(r) for r in cube.rotation_euler)
    print(f"Final rotation magnitude: {rotation_magnitude}")

    return rotation_magnitude < 0.001

def main():
    """Main test function"""
    print("Starting Apply Modifications Test")
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Current working directory: {os.getcwd()}")

    # Create test file
    test_file = create_test_blend_file()

    # Test standard apply rotation
    success1 = test_apply_rotation(test_file)

    # Test our operator logic
    success2 = test_our_operator_logic(test_file)

    print(f"\n=== RESULTS ===")
    print(f"Standard apply rotation: {'PASS' if success1 else 'FAIL'}")
    print(f"Our operator logic: {'PASS' if success2 else 'FAIL'}")

    # Clean up
    try:
        os.remove(test_file)
        print(f"Cleaned up test file: {test_file}")
    except:
        pass

if __name__ == "__main__":
    main()