# blender/panel.py

import bpy
from bpy.types import Panel

class SSTOOL_PT_MainPanel(bpy.types.Panel):
	"""
	Sidebar panel to open the SS Toolbox popup.

	Appears in the 3D Viewport under the 'Tool' tab.
	"""

	bl_label = "SS Toolbox"
	bl_idname = "SSTOOL_PT_MainPanel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tool'  # This will place the panel under the "Tool" tab

	def draw(self, context):
		layout = self.layout
		layout.operator("sstool.fbx2glb_popup", text="FBX to GLB Converter", icon='FILE_3D')
		layout.separator()
		layout.operator("sstool.glb2blend_popup", text="GLB to Blend Converter", icon='FILE_3D')
		layout.separator()
		layout.operator("sstool.file_sorter_popup", text="Open Sort Tool", icon='FILE_FOLDER')
		
		layout.separator()
		layout.operator("sstool.clean_blend_popup", text="Clean Blend for Godot", icon='FILE_REFRESH')

		layout.separator()
		layout.operator("sstool.simplify_materials_popup", text="Simplify Materials", icon='SHADING_TEXTURE')
