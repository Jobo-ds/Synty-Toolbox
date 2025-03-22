
bl_info = {
    "name": "Converter for Synty Sourcefiles",
    "author": "Joe",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Asset Tools",
    "description": "Converts sourcefiles from Synty Studios to GLB.",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    importlib.reload(main)
else:
    from . import main

def register():
    main.register()

def unregister():
    main.unregister()
