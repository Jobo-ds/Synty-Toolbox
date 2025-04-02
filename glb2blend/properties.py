import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import PropertyGroup

class GLB2BLENDProperties(PropertyGroup):
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