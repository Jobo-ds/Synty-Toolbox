#!/usr/bin/env python3
"""
Test the full Apply Modifications workflow exactly as it would run
"""

import bpy
import os
import sys
import mathutils

# Add the addon path to sys.path so we can import our modules
addon_path = os.path.dirname(__file__)
if addon_path not in sys.path:
    sys.path.append(addon_path)

def test_full_workflow():
    """Test the complete workflow including property setting"""

    print("=== Testing Full Apply Modifications Workflow ===")

    # Create a test file with rotated cube
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.name = "TestCube"
    cube.rotation_euler = (0.5, 1.0, 1.5)

    test_file = os.path.join(addon_path, "test_workflow.blend")
    bpy.ops.wm.save_as_mainfile(filepath=test_file)

    print(f"Created test file with rotated cube: {cube.rotation_euler}")

    # Now simulate our operator workflow
    try:
        # Import our operator
        from applymodifications.operator import SSTOOL_OT_ApplyModificationsOperator
        from applymodifications.properties import SSTOOL_PG_ApplyModificationsProperties

        # Register the properties temporarily
        bpy.utils.register_class(SSTOOL_PG_ApplyModificationsProperties)
        bpy.types.Scene.applymodifications_props = bpy.props.PointerProperty(type=SSTOOL_PG_ApplyModificationsProperties)

        # Set up the properties
        props = bpy.context.scene.applymodifications_props
        props.input_dir = addon_path
        props.include_subfolders = False
        props.apply_location = False
        props.apply_rotation = True  # This is what we're testing
        props.apply_scale = False

        print(f"Set apply_rotation to: {props.apply_rotation}")

        # Create and run the operator
        operator = SSTOOL_OT_ApplyModificationsOperator()
        result = operator.execute(bpy.context)

        print(f"Operator result: {result}")

        # Check if the rotation was applied by reloading the test file
        bpy.ops.wm.open_mainfile(filepath=test_file)
        cube = bpy.data.objects.get("TestCube")

        if cube:
            rotation_magnitude = sum(abs(r) for r in cube.rotation_euler)
            print(f"Final rotation after operator: {cube.rotation_euler}")
            print(f"Rotation magnitude: {rotation_magnitude}")

            if rotation_magnitude < 0.001:
                print("SUCCESS: Rotation was applied by our operator!")
                success = True
            else:
                print("FAILURE: Rotation was NOT applied by our operator!")
                success = False
        else:
            print("ERROR: Could not find test cube after operator")
            success = False

        # Clean up
        bpy.utils.unregister_class(SSTOOL_PG_ApplyModificationsProperties)
        del bpy.types.Scene.applymodifications_props

        try:
            os.remove(test_file)
        except:
            pass

        return success

    except Exception as e:
        print(f"ERROR in workflow test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_property_access():
    """Test if we can access the properties correctly"""

    print("\n=== Testing Property Access ===")

    try:
        from applymodifications.properties import SSTOOL_PG_ApplyModificationsProperties

        # Register the properties
        bpy.utils.register_class(SSTOOL_PG_ApplyModificationsProperties)
        bpy.types.Scene.applymodifications_props = bpy.props.PointerProperty(type=SSTOOL_PG_ApplyModificationsProperties)

        # Test property access
        props = bpy.context.scene.applymodifications_props

        print(f"Default apply_location: {props.apply_location}")
        print(f"Default apply_rotation: {props.apply_rotation}")
        print(f"Default apply_scale: {props.apply_scale}")

        # Set and read back
        props.apply_rotation = True
        print(f"Set apply_rotation to True, now reads: {props.apply_rotation}")

        # Clean up
        bpy.utils.unregister_class(SSTOOL_PG_ApplyModificationsProperties)
        del bpy.types.Scene.applymodifications_props

        return True

    except Exception as e:
        print(f"ERROR in property test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Starting Full Workflow Test")
    print(f"Addon path: {addon_path}")
    print(f"sys.path includes addon: {addon_path in sys.path}")

    # Test property access first
    prop_success = test_property_access()

    # Test full workflow
    workflow_success = test_full_workflow()

    print(f"\n=== FINAL RESULTS ===")
    print(f"Property access test: {'PASS' if prop_success else 'FAIL'}")
    print(f"Full workflow test: {'PASS' if workflow_success else 'FAIL'}")

if __name__ == "__main__":
    main()