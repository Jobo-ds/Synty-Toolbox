import bpy
import os
from bpy.types import Operator
from .state import flagged_complex_materials, generated_material_counter
from .fbx_handler import create_output_folder, get_fbx_files_in_folder, clear_scene, import_fbx, export_as_glb
from .material_utils import assign_new_generated_material


class ASSET_OT_ProcessFBX(Operator):
	"""
	Operator to process Synty FBX source files into GLB format.

	This operator imports all FBX files from a specified folder, assigns clean 
	generated materials to each mesh object using a chosen texture, and exports 
	each processed file as a GLB.
	"""	

	bl_idname = "asset.process_synty_sourcefiles"
	bl_label = "Process FBX Files"
	bl_description = "Imports FBX files, creates fresh materials, and exports as GLB"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		"""
		Executes the FBX to GLB conversion process.

		Validates the input folder and texture file, then iterates over all FBX files
		in the folder. For each file, it imports the FBX, replaces its materials, 
		and exports the result as a GLB. Shows a summary popup if complex materials are found.

		Returns:
			{'FINISHED'} if processing completes successfully, otherwise {'CANCELLED'}.
		"""

		settings = context.scene.asset_processor_settings
		input_folder = settings.fbx_folder
		texture_file = settings.texture_file

		if not os.path.isdir(input_folder):
			self.report({'ERROR'}, "Invalid FBX folder")
			return {'CANCELLED'}

		if not os.path.isfile(texture_file):
			self.report({'ERROR'}, "Invalid texture file")
			return {'CANCELLED'}

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

			# Assign new generated material to each mesh object
			for obj in bpy.context.scene.objects:
				if obj.type == 'MESH':
					assign_new_generated_material(obj, texture_file)

			export_as_glb(fbx_file, output_folder)

		self.report({'INFO'}, f"Processed {len(fbx_files)} file(s).")
		clear_scene()
		global generated_material_counter
		generated_material_counter = 0

		if flagged_complex_materials:
			bpy.ops.asset.debug_summary('INVOKE_DEFAULT')

		return {'FINISHED'}