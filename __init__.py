import bpy  # type: ignore # noqa: F401
from . import register_classes

bl_info = {
	"name": "Converter for Synty Sourcefiles",
	"author": "Joe",
	"version": (1, 0, 0),
	"blender": (2, 93, 0),
	"location": "View3D > Sidebar > Asset Tools",
	"description": "Toolbox for working with Synty Files.",
	"category": "Import-Export",
}

def register():
    register_classes.register()

def unregister():
    register_classes.unregister()
