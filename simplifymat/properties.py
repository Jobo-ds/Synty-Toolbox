import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_SimplifyMatProperties(PropertyGroup):
	simplifymat_dir: StringProperty(
		name="Input Directory",
		description="Root folder containing Blend or GLB files",
		subtype='DIR_PATH'
	) # type: ignore	