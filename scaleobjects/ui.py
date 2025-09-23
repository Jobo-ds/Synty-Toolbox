import bpy

class SSTOOL_OT_ScaleObjectsPopup(bpy.types.Operator):
	bl_idname = "sstool.scale_objects_popup"
	bl_label = "Scale Objects Settings"

	def execute(self, context):
		# Trigger the actual scale objects operator
		bpy.ops.sstool.scale_objects('INVOKE_DEFAULT')
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=400)

	def draw(self, context):
		layout = self.layout

		# Test if properties exist
		if not hasattr(context.scene, 'scaleobjects_props'):
			layout.label(text="ERROR: Properties not registered!", icon='ERROR')
			return

		props = context.scene.scaleobjects_props

		# Input directory
		layout.prop(props, "input_dir")
		layout.prop(props, "include_subfolders")

		layout.separator()

		# Scale factor
		layout.label(text="Scale Factor:", icon='TRANSFORM_SCALE')
		layout.prop(props, "scale_factor", text="")

		layout.separator()

		# Apply option
		layout.prop(props, "apply_after_scaling")