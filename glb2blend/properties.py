import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_GLB2BlendProperties(PropertyGroup):
	input_dir: StringProperty(
		name="Input Directory",
		description="Root folder containing GLB files",
		subtype='DIR_PATH'
	) # type: ignore	
	
	output_dir: StringProperty(
		name="Output Directory",
		description="Where .blend files will be saved",
		subtype='DIR_PATH'
	) # type: ignore	

	use_col_suffix: bpy.props.BoolProperty(
		name="Add '-col' to object names",
		description="If enabled, '-col' will be appended to all object names after import",
		default=False
	) # type: ignore
