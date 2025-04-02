# blender/converter_popup.py

import bpy
from bpy.props import BoolProperty, StringProperty

class SSTOOL_OT_FBX2BlendPopup(bpy.types.Operator):
	bl_idname = "sstool.fbx2glb_popup"
	bl_label = "FBX to GLB Converter"

	texture_file: StringProperty(name="Texture File", subtype='FILE_PATH')
	input_folder: StringProperty(name="Input Folder", subtype='DIR_PATH')
	normal_map_file: StringProperty(name="Normal Map", subtype='FILE_PATH')

	def execute(self, context):
		settings = context.scene.fbx2gbl_props

		# Store popup values into scene settings
		settings.texture_file = self.texture_file
		settings.normal_map_file = self.normal_map_file
		settings.fbx_folder = self.input_folder

		# Now invoke the processing operator
		bpy.ops.sstool.fbx2glb_converter('INVOKE_DEFAULT')

		return {'FINISHED'}

	def invoke(self, context, event):
		"""
		Pre-fills popup fields with values from the scene settings.
		"""

		settings = context.scene.fbx2gbl_props
		self.texture_file = settings.texture_file
		self.normal_map_file = settings.normal_map_file
		self.input_folder = settings.fbx_folder

		return context.window_manager.invoke_props_dialog(self, width=600)

	def draw(self, context):
		layout = self.layout
		props = context.scene.fbx2gbl_props

		layout.label(text="Settings for the conversion depend on the state of the meshes you need to convert.")

		# --- Input Section ---
		layout.label(text="📂 Input")
		box = layout.box()
		

		row = box.row()
		split = row.split(factor=0.8, align=True)
		split.prop(self, "input_folder", text="FBX Folder to Process")
		split.prop(props, "search_subfolders", text="Process subfolders")

		row = box.row()
		box.prop(props, "output_root_folder", text="Output Folder (optional)")

		row = box.row()
		split = row.split(factor=0.8, align=True)
		split.prop(self, "texture_file", text="Base Color Texture")
		split.prop(props, "auto_find_texture", text="Auto-detect")
		box.label(text="Base texture to apply to all FBX files in folder.", icon='INFO')

		row = box.row()
		split = row.split(factor=0.8, align=True)
		split.prop(self, "normal_map_file", text="Normal Map")
		split.prop(props, "auto_find_normal", text="Auto-detect")
		box.label(text="Normal map to add to all FBX files in folder.", icon='INFO')

		# --- Mesh Options ---
		layout.label(text="🧱 Mesh Options")
		box = layout.box()
		box.prop(props, "inherit_material_values", text="Inherit original material values")
		box.label(text="Base the new material on the original values.", icon='INFO')

		box.prop(props, "character_rotate_fix", text="Rotate armatures/character meshes")
		box.label(text="Rotates armatures 90° to stand up.", icon='INFO')

		box.prop(props, "force_texture", text="Force texture and normal map")
		box.label(text="Force texture and normal map to be added to all meshes.", icon='INFO')

		box.prop(props, "auto_normalize_scale", text="Attempt to normalize mesh scale")
		box.label(text="Attempt to detect and normalize mesh scale.", icon='INFO')

		# --- Extras ---
		layout.label(text="✨ Extras")
		box = layout.box()
		box.prop(props, "use_emission", text="Add Emission Texture")
		box.label(text="If your thumbnails are dark, an emission texture can light them up. Remove before using in games.", icon='INFO')

		box.prop(props, "use_error_material", text="Use Error Material")
		box.label(text="Any material errors will instead add bright red to the mesh.", icon='INFO')

		box.prop(props, "remove_clutter", text="Remove Clutter")
		box.label(text="Removes clutter left over from conversion in mesh.", icon='INFO')
