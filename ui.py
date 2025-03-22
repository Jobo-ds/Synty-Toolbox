import bpy
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


# UI Panel
class ASSET_PT_ProcessorPanel(Panel):
	bl_label = "FBX Asset Processor"
	bl_idname = "ASSET_PT_processor_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Asset Tools'

	def draw(self, context):
		layout = self.layout
		settings = context.scene.asset_processor_settings

		layout.prop(settings, "fbx_folder")
		layout.prop(settings, "texture_file")
		layout.operator("asset.process_synty_sourcefiles", text="Process FBX Files")




# ------------------------- Init

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
		for name, obj, count in state.flagged_complex_materials:
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

