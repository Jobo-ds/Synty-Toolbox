import bpy
import os
from bpy.types import Operator
from ..utils.blender import clear_scene

class SSTOOL_OT_ApplyModificationsOperator(Operator):
	bl_idname = "sstool.apply_modifications"
	bl_label = "Apply Modifications"
	bl_description = "Apply location, rotation, and scale modifications to objects in Blend files"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		print("[DEBUG] Apply Modifications operator started")
		props = context.scene.applymodifications_props

		input_dir = getattr(props, 'input_dir', '')
		apply_location = getattr(props, 'apply_location', False)
		apply_rotation = getattr(props, 'apply_rotation', False)
		apply_scale = getattr(props, 'apply_scale', False)

		print(f"[DEBUG] Input directory: '{input_dir}'")
		print(f"[DEBUG] Apply location: {apply_location}")
		print(f"[DEBUG] Apply rotation: {apply_rotation}")
		print(f"[DEBUG] Apply scale: {apply_scale}")

		if not input_dir or not os.path.exists(input_dir):
			self.report({'ERROR'}, f"Input directory not found: '{input_dir}'")
			return {'CANCELLED'}

		if not any([apply_location, apply_rotation, apply_scale]):
			self.report({'ERROR'}, "Select at least one transformation to apply")
			return {'CANCELLED'}

		processed_count = 0
		error_count = 0

		# Walk through directory
		if props.include_subfolders:
			file_iterator = os.walk(input_dir)
		else:
			# Only process files in the root directory
			root_files = []
			if os.path.exists(input_dir):
				for file in os.listdir(input_dir):
					file_path = os.path.join(input_dir, file)
					if os.path.isfile(file_path):
						root_files.append((input_dir, [], [file]))
			file_iterator = root_files

		for root, dirs, files in file_iterator:
			for file in files:
				if file.endswith('.blend'):
					filepath = os.path.join(root, file)
					try:
						if self.process_blend_file(filepath, apply_location, apply_rotation, apply_scale):
							processed_count += 1
							self.report({'INFO'}, f"Processed: {file}")
						else:
							error_count += 1
							self.report({'WARNING'}, f"No objects to process in: {file}")
					except Exception as e:
						error_count += 1
						self.report({'ERROR'}, f"Failed to process {file}: {str(e)}")
					finally:
						clear_scene()

		if processed_count > 0:
			self.report({'INFO'}, f"Successfully processed {processed_count} files")
		if error_count > 0:
			self.report({'WARNING'}, f"{error_count} files had errors")

		return {'FINISHED'}

	def process_blend_file(self, filepath, apply_location, apply_rotation, apply_scale):
		"""Process a single blend file and apply modifications"""
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

		# Convert quaternion rotation mode to Euler for better compatibility
		for obj in mesh_objects:
			if obj.rotation_mode == 'QUATERNION':
				print(f"[DEBUG] Converting {obj.name} from QUATERNION to XYZ rotation mode")
				obj.rotation_mode = 'XYZ'

		# Select all mesh objects for applying transformations
		bpy.ops.object.select_all(action='DESELECT')
		for obj in mesh_objects:
			obj.select_set(True)

		# Set active object and ensure context is properly set
		if mesh_objects:
			bpy.context.view_layer.objects.active = mesh_objects[0]

			# Force update the view layer
			bpy.context.view_layer.update()

		# Apply transformations based on user selection
		transformations_applied = []

		if apply_location:
			try:
				result = bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
				if result == {'FINISHED'}:
					transformations_applied.append("location")
					print(f"[APPLY_MODS] Applied location transformation")
				elif result == {'CANCELLED'}:
					# Manual location apply fallback
					for obj in mesh_objects:
						if obj.select_get():
							print(f"[DEBUG] Manually applying location for {obj.name}")
							print(f"  - Before: location = {obj.location}")

							# Only apply location if there actually is location to apply
							if any(abs(l) > 0.001 for l in obj.location):
								# Create a translation matrix from the object's location
								import mathutils
								translation_matrix = mathutils.Matrix.Translation(obj.location)

								# Apply the translation to the mesh data
								obj.data.transform(translation_matrix)

								# Reset the object's location
								obj.location = (0, 0, 0)

								print(f"  - Applied translation matrix to mesh data")
							else:
								print(f"  - No location to apply (already near zero)")

							print(f"  - After: location = {obj.location}")
							transformations_applied.append("location")
							print(f"[APPLY_MODS] Applied location transformation manually")
			except Exception as e:
				print(f"[ERROR] Failed to apply location: {e}")

		print(f"[DEBUG] Checking apply_rotation condition: {apply_rotation}")
		if apply_rotation:
			try:
				print(f"[DEBUG] About to apply rotation using bpy.ops.object.transform_apply...")
				result = bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
				print(f"[DEBUG] Apply rotation result: {result}")

				if result == {'FINISHED'}:
					transformations_applied.append("rotation")
					print(f"[APPLY_MODS] Applied rotation transformation")
				elif result == {'CANCELLED'}:
					print(f"[ERROR] bpy.ops.object.transform_apply was CANCELLED")
					print(f"[DEBUG] Trying manual rotation apply as fallback...")

					# Manual rotation apply as fallback
					for obj in mesh_objects:
						if obj.select_get():
							print(f"[DEBUG] Manually applying rotation for {obj.name}")
							print(f"  - Before: rotation = {obj.rotation_euler}")

							# Only apply rotation if there actually is rotation to apply
							if any(abs(r) > 0.001 for r in obj.rotation_euler):
								import mathutils

								# Apply rotation around the geometry center (not object origin)
								bpy.context.view_layer.objects.active = obj
								bpy.context.view_layer.update()

								if obj.mode != 'OBJECT':
									bpy.ops.object.mode_set(mode='OBJECT')

								# Get mesh center in object space (average of all vertices)
								mesh = obj.data
								if len(mesh.vertices) > 0:
									center = sum((v.co for v in mesh.vertices), mathutils.Vector()) / len(mesh.vertices)

									# Create transformation matrices
									rotation_matrix = obj.rotation_euler.to_matrix().to_4x4()

									# Transform around the mesh center: move to origin, rotate, move back
									translate_to_origin = mathutils.Matrix.Translation(-center)
									translate_back = mathutils.Matrix.Translation(center)
									final_transform = translate_back @ rotation_matrix @ translate_to_origin

									# Apply the transformation to mesh data
									mesh.transform(final_transform)
									mesh.update()

									print(f"  - Applied rotation around mesh center")
								else:
									print(f"  - No vertices in mesh to transform")

								# Reset only the rotation
								obj.rotation_euler = (0, 0, 0)
							else:
								print(f"  - No rotation to apply (already near zero)")

							print(f"  - After: rotation = {obj.rotation_euler}")
							transformations_applied.append("rotation")
							print(f"[APPLY_MODS] Applied rotation transformation manually")
				else:
					print(f"[WARNING] Unexpected result from rotation apply: {result}")
			except Exception as e:
				print(f"[ERROR] Failed to apply rotation: {e}")
				import traceback
				traceback.print_exc()
		else:
			print(f"[DEBUG] Skipping rotation apply because apply_rotation is {apply_rotation}")

		if apply_scale:
			try:
				result = bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
				if result == {'FINISHED'}:
					transformations_applied.append("scale")
					print(f"[APPLY_MODS] Applied scale transformation")
				elif result == {'CANCELLED'}:
					# Manual scale apply fallback
					for obj in mesh_objects:
						if obj.select_get():
							print(f"[DEBUG] Manually applying scale for {obj.name}")
							print(f"  - Before: scale = {obj.scale}")

							# Only apply scale if there actually is scale to apply
							if any(abs(s - 1.0) > 0.001 for s in obj.scale):
								# Create a scale matrix from the object's scale
								import mathutils
								scale_matrix = mathutils.Matrix.Scale(obj.scale[0], 4, (1, 0, 0)) @ \
											   mathutils.Matrix.Scale(obj.scale[1], 4, (0, 1, 0)) @ \
											   mathutils.Matrix.Scale(obj.scale[2], 4, (0, 0, 1))

								# Apply the scale to the mesh data
								obj.data.transform(scale_matrix)

								# Reset the object's scale
								obj.scale = (1, 1, 1)

								print(f"  - Applied scale matrix to mesh data")
							else:
								print(f"  - No scale to apply (already 1,1,1)")

							print(f"  - After: scale = {obj.scale}")
							transformations_applied.append("scale")
							print(f"[APPLY_MODS] Applied scale transformation manually")
			except Exception as e:
				print(f"[ERROR] Failed to apply scale: {e}")

		print(f"[APPLY_MODS] Applied transformations: {', '.join(transformations_applied)}")

		# Check rotation values before saving
		for obj in mesh_objects:
			print(f"[DEBUG] Before save - {obj.name}: rotation = {obj.rotation_euler}")

		# Save the file
		print(f"[DEBUG] About to save file: {filepath}")
		try:
			result = bpy.ops.wm.save_mainfile(filepath=filepath)
			print(f"[DEBUG] Save result: {result}")
			print(f"[APPLY_MODS] Saved: {filepath}")
		except Exception as e:
			print(f"[ERROR] Failed to save file: {e}")
			return False

		return True