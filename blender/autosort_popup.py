# blender/autosort_popup.py
import bpy

class ASSET_OT_OpenSortPopup(bpy.types.Operator):
	bl_idname = "asset.open_sort_popup"
	bl_label = "Open Sort Tool"

	def execute(self, context):
		return {'FINISHED'}  # You’re not doing anything here yet

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self, width=400)

	def draw(self, context):
		layout = self.layout
		props = context.scene.asset_processor_settings
		layout.prop(props, "sort_folder")
		layout.operator("asset.sort_files_by_name", icon="FILE_FOLDER", text="Sort Files")
		
        