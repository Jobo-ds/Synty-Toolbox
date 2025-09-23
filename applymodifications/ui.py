import bpy

class SSTOOL_OT_ApplyModificationsPopup(bpy.types.Operator):
	bl_idname = "sstool.apply_modifications_popup"
	bl_label = "Apply Modifications Settings"

	def execute(self, context):
		# Trigger the actual apply modifications operator
		bpy.ops.sstool.apply_modifications('INVOKE_DEFAULT')
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=400)

	def draw(self, context):
		layout = self.layout

		# Test if properties exist
		if not hasattr(context.scene, 'applymodifications_props'):
			layout.label(text="ERROR: Properties not registered!", icon='ERROR')
			return

		props = context.scene.applymodifications_props

		# Input directory
		layout.prop(props, "input_dir")
		layout.prop(props, "include_subfolders")

		layout.separator()

		# Transformation options
		layout.label(text="Apply Transformations (Make Permanent):", icon='MODIFIER_ON')
		col = layout.column(align=True)
		col.prop(props, "apply_location")
		col.prop(props, "apply_rotation")
		col.prop(props, "apply_scale")

