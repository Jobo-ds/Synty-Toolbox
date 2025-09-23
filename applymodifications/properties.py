import bpy
from bpy.props import BoolProperty, StringProperty, FloatVectorProperty, FloatProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_ApplyModificationsProperties(PropertyGroup):
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

	apply_location: BoolProperty(
		name="Apply Location",
		description="Apply location transformations to objects",
		default=False
	) # type: ignore

	apply_rotation: BoolProperty(
		name="Apply Rotation",
		description="Apply rotation transformations to objects",
		default=False
	) # type: ignore

	apply_scale: BoolProperty(
		name="Apply Scale",
		description="Apply scale transformations to objects",
		default=False
	) # type: ignore