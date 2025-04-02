import bpy # type: ignore

from .main_panel import SSTOOL_PT_MainPanel

from .filesorter.ui import SSTOOL_OT_FileSorterPopup
from .filesorter.properties import SSTOOL_PG_FileSorterProperties
from .filesorter.operator import SSTOOL_OT_SortFilesToFolders

from .fbx2glb.ui import SSTOOL_OT_FBX2BlendPopup
from .fbx2glb.properties import SSTOOL_PG_FBX2GLBProperties
from .fbx2glb.operator import SSTOOL_OT_FBX2GLBConverter
from .fbx2glb.utils.ascii_warning import SSTOOL_OT_ShowFbxAsciiDialog

from .glb2blend.ui import SSTOOL_OT_GLB2BlendPopup
from .glb2blend.properties import GLB2BLENDProperties
from .glb2blend.operator import ConvertGLBToBlendOperator



# Registration

main_classes = (
	SSTOOL_PT_MainPanel,
	SSTOOL_OT_ShowFbxAsciiDialog
)

filesorter_classes = (
	SSTOOL_OT_FileSorterPopup,
	SSTOOL_OT_SortFilesToFolders,
	SSTOOL_PG_FileSorterProperties	
)

fbx2glb_classes = (
	SSTOOL_OT_FBX2BlendPopup,
	SSTOOL_PG_FBX2GLBProperties,
	SSTOOL_OT_FBX2GLBConverter
)

glb2blend_classes = (
	SSTOOL_OT_GLB2BlendPopup,
	ConvertGLBToBlendOperator,
	GLB2BLENDProperties
)

classes = main_classes + filesorter_classes + fbx2glb_classes + glb2blend_classes

def register():
	"""
	Registers all classes and properties for the UI module.

	Called during addon registration to enable panels and popups.
	"""

	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.fbx2gbl_props = bpy.props.PointerProperty(type=SSTOOL_PG_FBX2GLBProperties)
	bpy.types.Scene.glb2blend_props = bpy.props.PointerProperty(type=GLB2BLENDProperties)
	bpy.types.Scene.filesorter_props = bpy.props.PointerProperty(type=SSTOOL_PG_FileSorterProperties)

def unregister():
	"""
	Unregisters all classes and properties defined in the UI module.

	Ensures a clean reload of the addon without leftover classes.
	"""

	for cls in reversed(classes):
		bpy.utils.register_class(cls)
	del bpy.types.Scene.fbx2gbl_props
	del bpy.types.Scene.glb2blend_props
	del bpy.types.Scene.filesorter_props
