import bpy

class SSTOOL_OT_SimplifyMatPopup(bpy.types.Operator):
    bl_idname = "sstool.simplify_materials_popup"
    bl_label = "Open Simplify Materials Popup"

    def execute(self, context):
        return {'FINISHED'}  # This popup doesn't do anything directly

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout
        props = context.scene.simplifymat_props

        layout.prop(props, "simplifymat_dir")
        layout.operator("sstool.simplify_materials", text="Simplify Now", icon='CHECKMARK')
