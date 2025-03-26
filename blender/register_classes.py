# blender/register_classes.py

import bpy
from .converter_popup import ASSET_OT_ConverterPopup
from .autosort_popup import ASSET_OT_OpenSortPopup
from .settings import AssetProcessorSettings
from .panel import ASSET_PT_ProcessorPanel

# Registration
classes = (
	AssetProcessorSettings,
	ASSET_PT_ProcessorPanel,
	ASSET_OT_ConverterPopup,
	ASSET_OT_OpenSortPopup
)

def register():
	"""
	Registers all classes and properties for the UI module.

	Called during addon registration to enable panels and popups.
	"""

	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.asset_processor_settings = bpy.props.PointerProperty(type=AssetProcessorSettings)

def unregister():
	"""
	Unregisters all classes and properties defined in the UI module.

	Ensures a clean reload of the addon without leftover classes.
	"""

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.asset_processor_settings
