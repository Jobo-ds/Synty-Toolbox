import bpy # type: ignore

from .main_panel import SSTOOL_PT_MainPanel

from .filesorter.ui import SSTOOL_OT_FileSorterPopup
from .filesorter.properties import SSTOOL_PG_FileSorterProperties
from .filesorter.operator import SSTOOL_OT_SortFilesOperator

from .fbx2glb.ui import SSTOOL_OT_FBX2BlendPopup
from .fbx2glb.properties import SSTOOL_PG_FBX2GLBProperties
from .fbx2glb.operator import SSTOOL_OT_FBX2GLBOperator
from .fbx2glb.test_operator import SSTOOL_OT_TestFBX2GLBOperator
from .fbx2glb.preview import SSTOOL_OT_PreviewBatchOperator
from .fbx2glb.utils.ascii_warning import SSTOOL_OT_ShowFbxAsciiDialog

from .glb2blend.ui import SSTOOL_OT_GLB2BlendPopup
from .glb2blend.properties import SSTOOL_PG_GLB2BlendProperties
from .glb2blend.operator import SSTOOL_OT_GLB2BlendOperator, SSTOOL_OT_TestGLB2BlendOperator

from .simplifymat.ui import SSTOOL_OT_SimplifyMatPopup
from .simplifymat.properties import SSTOOL_PG_SimplifyMatProperties
from .simplifymat.operator import SSTOOL_OT_SimplifyMatOperator

from .cleanblendforgodot.properties import SSTOOL_PG_CleanBlendProperties
from .cleanblendforgodot.operator import SSTOOL_OT_CleanBlendOperator
from .cleanblendforgodot.ui import SSTOOL_OT_CleanBlendPopup

from .applymodifications.ui import SSTOOL_OT_ApplyModificationsPopup
from .applymodifications.properties import SSTOOL_PG_ApplyModificationsProperties
from .applymodifications.operator import SSTOOL_OT_ApplyModificationsOperator

from .scaleobjects.ui import SSTOOL_OT_ScaleObjectsPopup
from .scaleobjects.properties import SSTOOL_PG_ScaleObjectsProperties
from .scaleobjects.operator import SSTOOL_OT_ScaleObjectsOperator



# Registration

main_classes = (
	SSTOOL_PT_MainPanel,
	SSTOOL_OT_ShowFbxAsciiDialog
)

filesorter_classes = (
	SSTOOL_OT_FileSorterPopup,
	SSTOOL_OT_SortFilesOperator,
	SSTOOL_PG_FileSorterProperties	
)

fbx2glb_classes = (
	SSTOOL_OT_FBX2BlendPopup,
	SSTOOL_OT_FBX2GLBOperator,
	SSTOOL_OT_TestFBX2GLBOperator,
	SSTOOL_OT_PreviewBatchOperator,
	SSTOOL_PG_FBX2GLBProperties
)

glb2blend_classes = (
	SSTOOL_OT_GLB2BlendPopup,
	SSTOOL_OT_GLB2BlendOperator,
	SSTOOL_OT_TestGLB2BlendOperator,
	SSTOOL_PG_GLB2BlendProperties
)

simpifymat_classes = (
	SSTOOL_OT_SimplifyMatPopup,
	SSTOOL_OT_SimplifyMatOperator,
	SSTOOL_PG_SimplifyMatProperties
)

cleanblend_classes = (
	SSTOOL_PG_CleanBlendProperties,  # must be registered BEFORE the pointer
	SSTOOL_OT_CleanBlendOperator,
	SSTOOL_OT_CleanBlendPopup,
)

applymodifications_classes = (
	SSTOOL_PG_ApplyModificationsProperties,  # must be registered BEFORE the pointer
	SSTOOL_OT_ApplyModificationsOperator,
	SSTOOL_OT_ApplyModificationsPopup,
)

scaleobjects_classes = (
	SSTOOL_PG_ScaleObjectsProperties,  # must be registered BEFORE the pointer
	SSTOOL_OT_ScaleObjectsOperator,
	SSTOOL_OT_ScaleObjectsPopup,
)

classes = main_classes + filesorter_classes + fbx2glb_classes + glb2blend_classes + simpifymat_classes + cleanblend_classes + applymodifications_classes + scaleobjects_classes

def register():
	"""
	Registers all classes and properties for the UI module.

	Called during addon registration to enable panels and popups.
	"""

	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.fbx2glb_props = bpy.props.PointerProperty(type=SSTOOL_PG_FBX2GLBProperties)
	bpy.types.Scene.glb2blend_props = bpy.props.PointerProperty(type=SSTOOL_PG_GLB2BlendProperties)
	bpy.types.Scene.filesorter_props = bpy.props.PointerProperty(type=SSTOOL_PG_FileSorterProperties)
	bpy.types.Scene.simplifymat_props = bpy.props.PointerProperty(type=SSTOOL_PG_SimplifyMatProperties)
	bpy.types.Scene.sstool_clean_blend_props = bpy.props.PointerProperty(type=SSTOOL_PG_CleanBlendProperties)
	bpy.types.Scene.applymodifications_props = bpy.props.PointerProperty(type=SSTOOL_PG_ApplyModificationsProperties)
	bpy.types.Scene.scaleobjects_props = bpy.props.PointerProperty(type=SSTOOL_PG_ScaleObjectsProperties)



def unregister():
	"""
	Unregisters all classes and properties defined in the UI module.

	Ensures a clean reload of the addon without leftover classes.
	"""


	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	if hasattr(bpy.types.Scene, "fbx2glb_props"):
		del bpy.types.Scene.fbx2glb_props
	if hasattr(bpy.types.Scene, "glb2blend_props"):
		del bpy.types.Scene.glb2blend_props
	if hasattr(bpy.types.Scene, "filesorter_props"):
		del bpy.types.Scene.filesorter_props
	if hasattr(bpy.types.Scene, "simplifymat_props"):
		del bpy.types.Scene.simplifymat_props
	if hasattr(bpy.types.Scene, "sstool_clean_blend_props"):
		del bpy.types.Scene.sstool_clean_blend_props
	if hasattr(bpy.types.Scene, "applymodifications_props"):
		del bpy.types.Scene.applymodifications_props
	if hasattr(bpy.types.Scene, "scaleobjects_props"):
		del bpy.types.Scene.scaleobjects_props
