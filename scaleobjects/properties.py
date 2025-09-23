import bpy
from bpy.props import BoolProperty, StringProperty, FloatVectorProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_ScaleObjectsProperties(PropertyGroup):
	input_dir: StringProperty(
		name="Input Directory",
		description="Root folder containing Blend files to process",
		subtype='DIR_PATH'
	) # type: ignore

	include_subfolders: BoolProperty(
		name="Include Subfolders",
		description="Process files in subfolders recursively",
		default=True
	) # type: ignore

	scale_factor: FloatVectorProperty(
		name="Scale Factor",
		description="Scale factor to apply to objects",
		default=(1.0, 1.0, 1.0),
		size=3,
		min=0.01,
		max=100.0
	) # type: ignore

	apply_after_scaling: BoolProperty(
		name="Apply Scale After Scaling",
		description="Apply the scale transformation after scaling (makes it permanent)",
		default=False
	) # type: ignore