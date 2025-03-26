# blender/converter_popup.py

import bpy
from bpy.props import BoolProperty, StringProperty

class ASSET_OT_ConverterPopup(bpy.types.Operator):
	"""
	Popup dialog for selecting input FBX folder and texture file.

	Stores input values into the scene settings and triggers processing.
	Also displays toggle options from the sidebar configuration.
	"""

	bl_idname = "asset.open_texture_folder_popup"
	bl_label = "Texture and Folder Inputs"

	texture_file: StringProperty(name="Texture File", subtype='FILE_PATH')
	input_folder: StringProperty(name="Input Folder", subtype='DIR_PATH')
	normal_map_file: StringProperty(name="Normal Map", subtype='FILE_PATH')

	def execute(self, context):
		settings = context.scene.asset_processor_settings

		# Store popup values into scene settings
		settings.texture_file = self.texture_file
		settings.normal_map_file = self.normal_map_file
		settings.fbx_folder = self.input_folder

		# Now invoke the processing operator
		bpy.ops.asset.process_synty_sourcefiles('INVOKE_DEFAULT')

		return {'FINISHED'}

	def invoke(self, context, event):
		"""
		Pre-fills popup fields with values from the scene settings.
		"""

		settings = context.scene.asset_processor_settings
		self.texture_file = settings.texture_file
		self.input_folder = settings.fbx_folder

		return context.window_manager.invoke_props_dialog(self, width=500)

	def draw(self, context):
		"""
		Draws the UI for the popup dialog, including path inputs and scene-linked options.
		"""

		layout = self.layout

		# Section: Header
		layout.label(text="🛠 Synty Sourcefile Converter", icon='FILE_3D')
		layout.separator()

		# Section: Input Paths
		box = layout.box()
		box.label(text="Input Files", icon='FOLDER_REDIRECT')
		box.prop(self, "input_folder", text="Input FBX Folder")
		box.prop(self, "texture_file", text="Base Color Texture")
		box.prop(context.scene.asset_processor_settings, "auto_find_texture")

		box.prop(self, "normal_map_file", text="Normal Map")
		box.prop(context.scene.asset_processor_settings, "auto_find_normal")

		# Section: Options (from scene settings)
		col = box.column(align=True)
		col.label(text="Options", icon='PREFERENCES')
		col.prop(context.scene.asset_processor_settings, "force_texture", text="Always apply texture")
		col.prop(context.scene.asset_processor_settings, "character_rotate_fix", text="Fix Character Rotation")
		col.prop(context.scene.asset_processor_settings, "auto_normalize_scale", text="Attempt to normalize scale of meshes")

		# Section: Footer
		layout.separator()
		layout.label(text="Click OK to start processing.", icon='INFO')