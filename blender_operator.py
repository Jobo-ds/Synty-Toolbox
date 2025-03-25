import bpy
import os
from bpy.types import Operator
from .state import flagged_complex_materials, generated_material_counter
from .fbx_handler import create_output_folder, get_fbx_files_in_folder, import_fbx, export_as_glb
from .material_utils import assign_new_generated_material, create_error_material
from .blender_utils import clear_scene


class ASSET_OT_ProcessFBX(Operator):
	"""
	Operator to process Synty FBX source files into GLB format.

	This operator imports all FBX files from a specified folder, assigns clean 
	generated materials to each mesh object using a chosen texture and optional normal map,
	and exports each processed file as a GLB.
	"""	
	
	bl_idname = "asset.process_synty_sourcefiles"
	bl_label = "Process FBX Files"
	bl_description = "Imports FBX files, creates fresh materials, and exports as GLB"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		settings = context.scene.asset_processor_settings
		input_folder = settings.fbx_folder
		texture_file = settings.texture_file
		normalmap_file = settings.normal_map_file

		# Auto-detect base color texture
		if not texture_file and settings.auto_find_texture:
			for filename in os.listdir(input_folder):
				if filename.lower().endswith(".png") and "normal" not in filename.lower():
					texture_file = os.path.join(input_folder, filename)
					print(f"[AUTO-TEXTURE] Using found texture: {texture_file}")
					break

		# Auto-detect normal map
		if not normalmap_file and settings.auto_find_normal:
			for filename in os.listdir(input_folder):
				if "normal" in filename.lower() and filename.lower().endswith(".png"):
					normalmap_file = os.path.join(input_folder, filename)
					print(f"[AUTO-NORMAL] Using found normal map: {normalmap_file}")
					break

		# Store updated values back to settings
		settings.texture_file = texture_file
		settings.normal_map_file = normalmap_file

		# Validate folder and texture requirements
		if not os.path.isdir(input_folder):
			self.report({'ERROR'}, "Invalid FBX folder")
			return {'CANCELLED'}

		if not texture_file and not normalmap_file:
			self.report({'WARNING'}, "No texture or normal map found — proceeding with base material only.")

		output_folder = create_output_folder(input_folder)
		if not output_folder:
			self.report({'ERROR'}, "Failed to create output folder")
			return {'CANCELLED'}

		fbx_files = get_fbx_files_in_folder(input_folder)
		if not fbx_files:
			self.report({'WARNING'}, "No FBX files found")
			return {'CANCELLED'}

		for fbx_file in fbx_files:
			print(f"\n[PROCESSING] {fbx_file}")
			clear_scene()
			import_fbx(fbx_file)

			# Assign generated materials
			for obj in bpy.context.scene.objects:
				if obj.type == 'MESH':
					assign_new_generated_material(obj, texture_file, normalmap_file)

			export_as_glb(fbx_file, output_folder)

		self.report({'INFO'}, f"Processed {len(fbx_files)} file(s).")
		clear_scene()

		global generated_material_counter
		generated_material_counter = 0

		if flagged_complex_materials:
			bpy.ops.asset.debug_summary('INVOKE_DEFAULT')

		if settings.auto_find_texture:
			settings.texture_file = ""
		if settings.auto_find_normal:
			settings.normal_map_file = ""

		return {'FINISHED'}
