import bpy

class SSTOOL_OT_FileSorterPopup(bpy.types.Operator):
	bl_idname = "sstool.file_sorter_popup"
	bl_label = "Open File Sort Tool"

	def execute(self, context):
		return {'FINISHED'}  # You’re not doing anything here yet

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self, width=400)

	def draw(self, context):
		layout = self.layout
		props = context.scene.filesorter_props

		layout.label(text="Select a folder of FBX files to sort into category folders:")
		layout.prop(props, "sort_folder")
		layout.operator("sstool.sort_files_to_folders", icon="FILE_FOLDER", text="Sort Files")
