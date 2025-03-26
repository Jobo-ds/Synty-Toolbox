# blender/settings.py

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import PropertyGroup

# Property Group to store settings
class AssetProcessorSettings(PropertyGroup):
	"""
	Holds all user-configurable options for the asset processor.

	Stored in the Scene to persist between Blender sessions.
	"""
	
	"""
		Inputs
	"""

	fbx_folder: StringProperty(
		name="FBX Folder",
		description="Folder containing FBX files to process",
		subtype='DIR_PATH'
	) # type: ignore
	
	texture_file: StringProperty(
		name="Base Color Texture",
		description="Optional texture to apply to material",
		subtype='FILE_PATH'
	) # type: ignore

	auto_find_texture: BoolProperty(
		name="Auto-detect texture",
		description="Search for a texture in the input folder if blank",
		default=True
	) # type: ignore

	normal_map_file: StringProperty(
		name="Normal Map",
		description="Optional normal map to apply to the material",
		subtype='FILE_PATH'
	 ) # type: ignore

	auto_find_normal: BoolProperty(
		name="Auto-detect normal map",
		description="Search for a normal map in the folder if none is provided",
		default=True
	) # type: ignore

	"""
		Mesh Options
	"""

	inherit_material_values: BoolProperty(
		name="Inherit Material Values",
		description="Base the new material on the original values.",
		default=True
	) # type: ignore	

	character_rotate_fix: BoolProperty(
		name="Character Rotate Fix",
		description="If your meshes are characters, rotate the mesh upright after import (e.g. if they appear face-down)",
		default=False
	) # type: ignore

	force_texture: BoolProperty(
		name="Always apply texture",
		description="Apply texture, regardless of original material.",
		default=False
	) # type: ignore

	auto_normalize_scale: BoolProperty(
		name="Attempt normalize scale of meshes",
		description="Attempt to rescale meshes by looking for small (x < 1cm) and large (x > 150m) meshes.",
		default=True
	) # type: ignore	


	"""
		Extras
	"""

	use_emission: BoolProperty(
		name="Add Emission Layer",
		description="Use an emission texture to brighten materials for thumbnails.",
		default=True
	) # type: ignore

	use_error_material: BoolProperty(
		name="Use Error Material",
		description="Use a bright red error material if something goes wrong.",
		default=True
	) # type: ignore

	remove_clutter: BoolProperty(
		name="Remove Clutter",
		description="Remove common import clutter (like 'iconosphere', 'root.001', etc.)",
		default=True
	) # type: ignore	

	"""
		Sort Folder
	"""	

	sort_folder: StringProperty(
		name="Sort Folder",
		description="Folder containing FBX files to sort",
		subtype='DIR_PATH',
	) # type: ignore	