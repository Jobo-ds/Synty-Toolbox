import bpy

class SSTOOL_OT_GLB2BlendPopup(bpy.types.Operator):
	bl_idname = "sstool.glb2blend_popup"
	bl_label = "Open GLB2Blend Popup"

	def execute(self, context):
		return {'FINISHED'}  # You’re not doing anything here yet

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self, width=400)

	def draw(self, context):
		layout = self.layout
		props = context.scene.glb2blend_props

		layout.prop(props, "input_dir")
		layout.prop(props, "output_dir")
		layout.prop(props, "use_col_suffix")
		layout.operator("object.convert_glb_to_blend")
		