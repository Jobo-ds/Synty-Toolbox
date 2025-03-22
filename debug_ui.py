import bpy
from .state import flagged_complex_materials, generated_material_counter

class ASSET_OT_DebugPrompt(bpy.types.Operator):
    bl_idname = "asset.debug_prompt"
    bl_label = "Complex Material Detected"
    bl_options = {'INTERNAL'}

    message: bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}  # Continue

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=500)  # Wider than default

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        for line in self.message.split("\n"):
            col.label(text=line)
        col.separator()
        row = col.row()
        row.operator("asset.debug_continue", text="Continue")
        row.operator("asset.debug_cancel", text="Cancel")

class ASSET_OT_DebugContinue(bpy.types.Operator):
    bl_idname = "asset.debug_continue"
    bl_label = "Continue Processing"

    def execute(self, context):
        print("[INFO] User chose to continue after debug prompt.")
        return {'FINISHED'}

class ASSET_OT_DebugCancel(bpy.types.Operator):
    bl_idname = "asset.debug_cancel"
    bl_label = "Cancel Processing"

    def execute(self, context):
        self.report({'WARNING'}, "Processing cancelled by user from summary popup.")
        return {'CANCELLED'}
    
def register_debug_operators():
    bpy.utils.register_class(ASSET_OT_DebugPrompt)
    bpy.utils.register_class(ASSET_OT_DebugContinue)
    bpy.utils.register_class(ASSET_OT_DebugCancel)

def unregister_debug_operators():
    bpy.utils.unregister_class(ASSET_OT_DebugPrompt)
    bpy.utils.unregister_class(ASSET_OT_DebugCancel)
    bpy.utils.unregister_class(ASSET_OT_DebugContinue)
