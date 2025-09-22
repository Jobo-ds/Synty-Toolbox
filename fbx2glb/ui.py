# blender/converter_popup.py

import bpy
from bpy.props import BoolProperty, StringProperty

class SSTOOL_OT_FBX2BlendPopup(bpy.types.Operator):
	bl_idname = "sstool.fbx2glb_popup"
	bl_label = "FBX to GLB Converter"

	texture_file: StringProperty(name="Texture File", subtype='FILE_PATH')
	input_folder: StringProperty(name="Input Folder", subtype='DIR_PATH')

	def execute(self, context):
		settings = context.scene.fbx2glb_props

		# Store popup values into scene settings
		settings.texture_file = self.texture_file
		settings.fbx_folder = self.input_folder

		# Now invoke the processing operator
		bpy.ops.sstool.fbx2glb_converter('INVOKE_DEFAULT')

		return {'FINISHED'}

	def invoke(self, context, event):
		"""
		Pre-fills popup fields with values from the scene settings.
		"""

		# Check if properties exist
		if not hasattr(context.scene, 'fbx2glb_props'):
			self.report({'ERROR'}, "Properties not found. Please restart Blender or reinstall the addon.")
			return {'CANCELLED'}

		try:
			settings = context.scene.fbx2glb_props
			self.texture_file = getattr(settings, 'texture_file', '')
			self.input_folder = getattr(settings, 'fbx_folder', '')
		except Exception as e:
			self.report({'ERROR'}, f"Error loading settings: {e}")
			return {'CANCELLED'}

		return context.window_manager.invoke_props_dialog(self, width=700)

	def draw(self, context):
		layout = self.layout

		# Check if properties exist
		if not hasattr(context.scene, 'fbx2glb_props'):
			layout.label(text="ERROR: Properties not found. Please restart Blender or reinstall the addon.", icon='ERROR')
			return

		props = context.scene.fbx2glb_props

		layout.label(text="FBX to GLB Converter Settings")

		# Main two-column layout
		split = layout.split(factor=0.5, align=True)
		left_col = split.column(align=True)
		right_col = split.column(align=True)

		# LEFT COLUMN
		# --- Input Section ---
		left_col.label(text="📂 Input", icon='NONE')
		box = left_col.box()
		box.prop(self, "input_folder", text="FBX Folder")
		box.prop(props, "search_subfolders", text="Process subfolders")
		box.prop(props, "output_root_folder", text="Output Folder")

		box.prop(self, "texture_file", text="Base Texture")
		box.prop(props, "auto_find_texture", text="Auto-detect texture")

		# --- Mesh Options ---
		left_col.separator()
		left_col.label(text="🧱 Mesh Options", icon='NONE')
		box = left_col.box()
		box.prop(props, "character_rotate_fix", text="Rotate armatures 90°")
		box.prop(props, "auto_normalize_scale", text="Auto normalize scale")
		box.prop(props, "reset_object_scale", text="Reset scale to 1.0")

		# --- Export Options ---
		left_col.separator()
		left_col.label(text="📦 Export", icon='NONE')
		box = left_col.box()
		box.prop(props, "export_format", text="Format")
		if props.export_format == 'GLB':
			box.prop(props, "embed_textures", text="Embed Textures")

		# RIGHT COLUMN
		# --- Processing Options ---
		right_col.label(text="⚙️ Processing", icon='NONE')
		box = right_col.box()
		box.prop(props, "continue_on_error", text="Continue on Error")

		row = box.row()
		row.prop(props, "retry_failed_imports", text="Retry Failed")
		if props.retry_failed_imports:
			row.prop(props, "max_retries", text="Max")

		box.prop(props, "clear_cache_between_folders", text="Clear Cache")
		box.prop(props, "validate_textures", text="Validate Textures")

		# --- Material Options ---
		right_col.separator()
		right_col.label(text="🎨 Material", icon='NONE')
		box = right_col.box()
		box.prop(props, "material_template", text="Template")

		if props.material_template == 'emissive':
			row = box.row()
			row.prop(props, "emission_strength", text="Strength")
			row.prop(props, "emission_factor", text="Factor")

		box.prop(props, "inherit_material_values", text="Inherit Values")
		box.prop(props, "force_texture", text="Force Texture")

		# --- Cleanup & Debugging ---
		right_col.separator()
		right_col.label(text="🧹 Cleanup", icon='NONE')
		box = right_col.box()
		box.prop(props, "use_error_material", text="Error Material")
		box.prop(props, "remove_clutter", text="Remove Clutter")
		box.prop(props, "show_processing_log", text="Detailed Log")
		box.prop(props, "thorough_scene_clear", text="Thorough Clear")
		box.prop(props, "use_legacy_materials", text="Legacy Materials")

		# Bottom buttons (full width)
		layout.separator()
		row = layout.row()
		row.scale_y = 1.2
		row.operator("sstool.preview_batch", text="Preview Batch", icon='VIEWZOOM')
		row.operator("sstool.test_fbx2glb_converter", text="Test Single File", icon='PLAY')
