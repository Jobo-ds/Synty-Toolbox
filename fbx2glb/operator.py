# blender_operator.py

import bpy
import os
from bpy.types import Operator
import pathlib

from ..state import generated_material_counter
from .importers.fbx import import_fbx
from .exporters.glb import export_as_glb
from .utils.material_operations import assign_new_generated_material
from ..utils.blender import clear_scene
from ..utils.file_operations import get_files_in_folder
from ..utils.folder_operations import create_output_folder, get_subfolders
from ..utils.memory import purge_unused_data
from ..simplifymat.operator import merge_duplicate_materials


class SSTOOL_OT_FBX2GLBOperator(Operator):
	bl_idname = "sstool.fbx2glb_converter"
	bl_label = "Process FBX Files"
	bl_description = "Imports FBX files, creates fresh materials, and exports as GLB"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		settings = context.scene.fbx2gbl_props
		input_folder = settings.fbx_folder

		folders_to_process = []

		if settings.search_subfolders:
			folders = get_subfolders(input_folder, "fbx")
			for folder in folders:
				folders_to_process.append(folder)
		else:
			folders_to_process.append(input_folder)		


		for folder in folders_to_process:
			texture_file = settings.texture_file if not settings.auto_find_texture else ""
			normalmap_file = settings.normal_map_file if not settings.auto_find_normal else ""

			# Auto-detect base color texture
			if not texture_file and settings.auto_find_texture:
				for filename in os.listdir(folder):
					if filename.lower().endswith(".png") and "normal" not in filename.lower():
						texture_file = os.path.join(folder, filename)
						print(f"[AUTO-TEXTURE] Using found texture: {texture_file}")
						break

			# Auto-detect normal map
			if not normalmap_file and settings.auto_find_normal:
				for filename in os.listdir(folder):
					if "normal" in filename.lower() and filename.lower().endswith(".png"):
						normalmap_file = os.path.join(folder, filename)
						print(f"[AUTO-NORMAL] Using found normal map: {normalmap_file}")
						break

			# Store updated values back to settings
			settings.texture_file = texture_file
			settings.normal_map_file = normalmap_file

			# Validate folder and texture requirements
			if not os.path.isdir(folder):
				self.report({'ERROR'}, "Invalid FBX folder")
				return {'CANCELLED'}

			if not texture_file and not normalmap_file:
				self.report({'WARNING'}, "No texture or normal map found — proceeding with base material only.")

			if settings.output_root_folder:
				relative_path = os.path.relpath(folder, input_folder)
				output_folder = os.path.join(settings.output_root_folder, relative_path)
				os.makedirs(output_folder, exist_ok=True)
			else:
				output_folder = create_output_folder(folder)
				
			if not output_folder:
				self.report({'ERROR'}, "Failed to create output folder")
				return {'CANCELLED'}

			fbx_files = get_files_in_folder(folder, "fbx")
			if not fbx_files:
				self.report({'WARNING'}, "No FBX files found")
				return {'CANCELLED'}

			for fbx_file in fbx_files:
				print(f"\n[PROCESSING] {fbx_file}")
				clear_scene()
				try:
					import_fbx(fbx_file)
				except RuntimeError as e:
					bpy.ops.sfc.fbx_ascii_dialog('INVOKE_DEFAULT', message=fbx_file)
					return {'CANCELLED'}


				# Assign generated materials
				for obj in bpy.context.scene.objects:
					if obj.type == 'MESH':
						assign_new_generated_material(obj, texture_file, normalmap_file)

				merge_duplicate_materials()
				export_as_glb(fbx_file, output_folder)
				global generated_material_counter
				generated_material_counter = 0

			self.report({'INFO'}, f"Processed {len(fbx_files)} file(s).")
			clear_scene()
			purge_unused_data()

			if settings.auto_find_texture:
				settings.texture_file = ""
			if settings.auto_find_normal:
				settings.normal_map_file = ""

		return {'FINISHED'}

