
bl_info = {
	"name": "Converter for Synty Sourcefiles",
	"author": "Joe",
	"version": (1, 0, 0),
	"blender": (2, 93, 0),
	"location": "View3D > Sidebar > Asset Tools",
	"description": "Converts sourcefiles from Synty Studios to GLB.",
	"category": "Import-Export",
}

import bpy
from .blender import register_classes
from .blender_operator import ASSET_OT_ProcessFBX
from . import file_sorter


def register():
    register_classes.register()
    bpy.utils.register_class(ASSET_OT_ProcessFBX)
    file_sorter.register()

def unregister():
    file_sorter.unregister()
    bpy.utils.unregister_class(ASSET_OT_ProcessFBX)
    register_classes.unregister()
