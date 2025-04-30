import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_CleanBlendProperties(PropertyGroup):
	blend_folder: StringProperty(
		name="Blend Folder",
		subtype='DIR_PATH'
	)
	image_path: StringProperty(
		name="Image File",
		subtype='FILE_PATH'
	)
	material_name: StringProperty(
		name="Base Material Name",
		default="Material"
	)
