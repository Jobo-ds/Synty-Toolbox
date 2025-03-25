
bl_info = {
	"name": "Converter for Synty Sourcefiles",
	"author": "Joe",
	"version": (1, 0, 0),
	"blender": (2, 93, 0),
	"location": "View3D > Sidebar > Asset Tools",
	"description": "Converts sourcefiles from Synty Studios to GLB.",
	"category": "Import-Export",
}

from . import blender_operator, ui, debug_ui, file_sorter

def register():
    ui.register()
    blender_operator.bpy.utils.register_class(blender_operator.ASSET_OT_ProcessFBX)
    file_sorter.register()
    debug_ui.register_debug_operators()

def unregister():
    debug_ui.unregister_debug_operators()
    file_sorter.unregister()
    blender_operator.bpy.utils.unregister_class(blender_operator.ASSET_OT_ProcessFBX)
    ui.unregister()
