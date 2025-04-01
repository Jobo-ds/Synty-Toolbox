# blender/panel.py

import bpy
from bpy.types import Panel

class ASSET_PT_ProcessorPanel(bpy.types.Panel):
	"""
	Sidebar panel to open the Synty Converter popup.

	Appears in the 3D Viewport under the 'Tool' tab.
	Provides a button to launch the interactive processing dialog.
	"""

	bl_label = "Synty FBX Source File Processor"
	bl_idname = "ASSET_PT_ProcessorPanel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tool'  # This will place the panel under the "Tool" tab

	def draw(self, context):
		layout = self.layout
		layout.operator("asset.open_texture_folder_popup", text="Open Synty Converter", icon='FILE_3D')
		layout.separator()
		layout.operator("asset.open_sort_popup", text="Open Sort Tool", icon='FILE_FOLDER')