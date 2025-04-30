import bpy
from bpy.types import Operator
from .operator import SSTOOL_OT_CleanBlendOperator

class SSTOOL_OT_CleanBlendPopup(Operator):
	bl_idname = "sstool.clean_blend_popup"
	bl_label = "Clean Blend for Godot"
	bl_options = {'REGISTER', 'UNDO'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		props = context.scene.sstool_clean_blend_props
		layout = self.layout
		layout.prop(props, "blend_folder")
		layout.prop(props, "image_path")
		layout.prop(props, "material_name")

	def execute(self, context):
		return bpy.ops.sstool.clean_blend_execute()
