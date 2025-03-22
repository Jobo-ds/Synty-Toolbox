import bpy
import os
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty
from .state import flagged_complex_materials, generated_material_counter

# Property Group to store settings
class AssetProcessorSettings(PropertyGroup):
	fbx_folder: StringProperty(
		name="FBX Folder",
		description="Folder containing FBX files to process",
		subtype='DIR_PATH'
	)

	texture_file: StringProperty(
		name="Texture Image",
		description="Base color texture to apply to models",
		subtype='FILE_PATH'
	)


# Button for opening the tool.
class ASSET_PT_ProcessorPanel(bpy.types.Panel):
	bl_label = "Synty Asset Processor"
	bl_idname = "ASSET_PT_ProcessorPanel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tool'  # This will place the panel under the "Tool" tab

	def draw(self, context):
		layout = self.layout
		layout.operator("asset.open_texture_folder_popup", text="Open Synty Converter")


# Pop-up Window
class ASSET_OT_OpenTextureFolderPopup(bpy.types.Operator):
	bl_idname = "asset.open_texture_folder_popup"
	bl_label = "Texture and Folder Inputs"

	texture_file: StringProperty(name="Texture File", subtype='FILE_PATH')
	input_folder: StringProperty(name="Input Folder", subtype='DIR_PATH')

	def execute(self, context):
		if not os.path.isfile(self.texture_file):
			self.report({'ERROR'}, "Please select a valid texture file.")
			return {'CANCELLED'}

		if not os.path.isdir(self.input_folder):
			self.report({'ERROR'}, "Please select a valid FBX folder.")
			return {'CANCELLED'}

		# Store values in the Scene's settings for the actual processor to use
		settings = context.scene.asset_processor_settings
		settings.texture_file = self.texture_file
		settings.fbx_folder = self.input_folder

		bpy.ops.asset.process_synty_sourcefiles('INVOKE_DEFAULT')
		return {'FINISHED'}


	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self, width=500)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "texture_file")
		layout.prop(self, "input_folder")
		layout.label(text="Click OK to start processing.")


# Debug Summary Window
class ASSET_OT_DebugSummary(bpy.types.Operator):
	bl_idname = "asset.debug_summary"
	bl_label = "Complex Materials Found"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		print("[INFO] User chose to continue after debug summary.")
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_popup(self, width=600)

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.label(text="Some materials in the processed files may be complex:")
		col.separator()
		for name, obj, count in flagged_complex_materials:
			col.label(text=f"Material '{name}' on object '{obj}' has {count} nodes.")
		col.separator()
		row = col.row()
		row.operator("asset.debug_summary_continue", text="Continue")
		row.operator("asset.debug_summary_cancel", text="Cancel")


class ASSET_OT_DebugSummaryContinue(bpy.types.Operator):
	bl_idname = "asset.debug_summary_continue"
	bl_label = "Continue Processing"

	def execute(self, context):
		return {'FINISHED'}


class ASSET_OT_DebugSummaryCancel(bpy.types.Operator):
	bl_idname = "asset.debug_summary_cancel"
	bl_label = "Cancel Processing"

	def execute(self, context):
		print("[INFO] User canceled processing from debug summary.")
		raise SystemExit("Stopped by user from summary popup.")


# Registration
classes = (
	AssetProcessorSettings,
	ASSET_PT_ProcessorPanel,
	ASSET_OT_OpenTextureFolderPopup,
	ASSET_OT_DebugSummary,
	ASSET_OT_DebugSummaryContinue,
	ASSET_OT_DebugSummaryCancel,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.asset_processor_settings = bpy.props.PointerProperty(type=AssetProcessorSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.asset_processor_settings
