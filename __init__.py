
bl_info = {
	"name": "Converter for Synty Sourcefiles",
	"author": "Joe",
	"version": (1, 0, 0),
	"blender": (2, 93, 0),
	"location": "View3D > Sidebar > Asset Tools",
	"description": "Converts sourcefiles from Synty Studios to GLB.",
	"category": "Import-Export",
}

from . import blender_operator, ui, debug_ui
import bpy

def register():
	ui.bpy.utils.register_class(ui.AssetProcessorSettings)
	ui.bpy.types.Scene.asset_processor_settings = ui.bpy.props.PointerProperty(type=ui.AssetProcessorSettings)

	blender_operator.bpy.utils.register_class(blender_operator.ASSET_OT_ProcessFBX)
	ui.bpy.utils.register_class(ui.ASSET_PT_ProcessorPanel)
	ui.bpy.utils.register_class(ui.ASSET_OT_OpenTextureFolderPopup)
	ui.bpy.utils.register_class(ui.ASSET_OT_ReloadAddon)


	debug_ui.register_debug_operators()


def unregister():
	debug_ui.unregister_debug_operators()
	
	ui.bpy.utils.unregister_class(ui.ASSET_PT_ProcessorPanel)
	blender_operator.bpy.utils.unregister_class(blender_operator.ASSET_OT_ProcessFBX)
	ui.bpy.utils.unregister_class(ui.ASSET_OT_OpenTextureFolderPopup)
	ui.bpy.utils.unregister_class(ui.ASSET_OT_ReloadAddon)


	del ui.bpy.types.Scene.asset_processor_settings

	try:
		ui.bpy.utils.unregister_class(ui.AssetProcessorSettings)
	except RuntimeError:
		pass
