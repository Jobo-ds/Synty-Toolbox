import bpy
import os
from bpy.types import Operator
from ..utils.blender import clear_scene

class SSTOOL_OT_ScaleObjectsOperator(Operator):
	bl_idname = "sstool.scale_objects"
	bl_label = "Scale Objects"
	bl_description = "Scale objects in Blend files by a specified factor"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		props = context.scene.scaleobjects_props

		if not props.input_dir or not os.path.exists(props.input_dir):
			self.report({'ERROR'}, "Input directory not found")
			return {'CANCELLED'}

		scale_values = (props.scale_factor[0], props.scale_factor[1], props.scale_factor[2])
		if scale_values == (1.0, 1.0, 1.0):
			self.report({'ERROR'}, "Scale factor is (1,1,1) - no scaling will occur")
			return {'CANCELLED'}

		processed_count = 0
		error_count = 0

		# Walk through directory
		if props.include_subfolders:
			file_iterator = os.walk(props.input_dir)
		else:
			# Only process files in the root directory
			root_files = []
			if os.path.exists(props.input_dir):
				for file in os.listdir(props.input_dir):
					file_path = os.path.join(props.input_dir, file)
					if os.path.isfile(file_path):
						root_files.append((props.input_dir, [], [file]))
			file_iterator = root_files

		for root, dirs, files in file_iterator:
			for file in files:
				if file.endswith('.blend'):
					filepath = os.path.join(root, file)
					try:
						if self.process_blend_file(filepath, props):
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
			self.report({'INFO'}, f"Successfully scaled objects in {processed_count} files")
		if error_count > 0:
			self.report({'WARNING'}, f"{error_count} files had errors")

		return {'FINISHED'}

	def process_blend_file(self, filepath, props):
		"""Process a single blend file and scale objects"""
		print(f"[SCALE_OBJECTS] Processing: {filepath}")

		# Clear scene first
		clear_scene()

		# Open the blend file
		bpy.ops.wm.open_mainfile(filepath=filepath)

		# Get all mesh objects
		mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

		if not mesh_objects:
			print(f"[SCALE_OBJECTS] No mesh objects found in {filepath}")
			return False

		# Apply scale factor to all mesh objects
		scale_factor = props.scale_factor
		scale_values = (scale_factor[0], scale_factor[1], scale_factor[2])

		for obj in mesh_objects:
			obj.scale = (
				obj.scale[0] * scale_factor[0],
				obj.scale[1] * scale_factor[1],
				obj.scale[2] * scale_factor[2]
			)

		print(f"[SCALE_OBJECTS] Applied scale factor: {scale_values}")

		# Apply scale transformation if requested (make it permanent)
		if props.apply_after_scaling:
			# Select all mesh objects
			bpy.ops.object.select_all(action='DESELECT')
			for obj in mesh_objects:
				obj.select_set(True)

			# Set active object
			if mesh_objects:
				bpy.context.view_layer.objects.active = mesh_objects[0]

			try:
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
				print(f"[SCALE_OBJECTS] Applied scale transformation (made permanent)")
			except Exception as e:
				print(f"[ERROR] Failed to apply scale: {e}")

		# Save the file
		bpy.ops.wm.save_mainfile(filepath=filepath)
		print(f"[SCALE_OBJECTS] Saved: {filepath}")

		return True