import bpy

class SFC_OT_fbx_ascii_dialog(bpy.types.Operator):
    bl_idname = "sfc.fbx_ascii_dialog"
    bl_label = "ASCII FBX Not Supported"

    message: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        col = self.layout.column()
        col.label(text="❌ ASCII FBX file detected", icon='ERROR')
        col.label(text="This FBX file is not supported:")
        col.label(text=self.message)
        col.separator()
        col.label(text="Use Autodesk FBX Converter to convert it to binary.")
        col.label(text="Google it.")

    def execute(self, context):
        return {'FINISHED'}
