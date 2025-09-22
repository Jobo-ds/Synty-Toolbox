import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, FloatProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_FBX2GLBProperties(PropertyGroup):
	
	# Inputs

	fbx_folder: StringProperty(
		name="FBX Folder",
		description="Folder containing FBX files to process",
		subtype='DIR_PATH'
	) # type: ignore

	search_subfolders: BoolProperty(
		name="Search Subfolders",
		description="Search recursively through subfolders for FBX files",
		default=False
	) # type: ignore	

	output_root_folder: StringProperty(
		name="Output Folder",
		description="If no output folder is set, it uses the input folder.",
		subtype='DIR_PATH',
		default=""
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

	#Mesh Options

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

	reset_object_scale: BoolProperty(
		name="Reset object scale to 1.0",
		description="Set all object scales directly to (1.0, 1.0, 1.0) - useful for tiny 0.01 scaled objects",
		default=True
	) # type: ignore	

	# Material Template

	material_template: EnumProperty(
		name="Material Template",
		description="Template to use for material creation",
		items=[
			('standard', 'Standard PBR', 'Standard physically based material'),
			('emissive', 'Emissive (Thumbnails)', 'PBR material with emission for bright thumbnails'),
			('stylized', 'Stylized', 'Stylized material for artistic rendering'),
		],
		default='standard'
	) # type: ignore

	# Processing Options

	continue_on_error: BoolProperty(
		name="Continue on Error",
		description="Continue processing remaining files if one fails",
		default=True
	) # type: ignore

	retry_failed_imports: BoolProperty(
		name="Retry Failed Imports",
		description="Retry importing files that fail on first attempt",
		default=True
	) # type: ignore

	max_retries: IntProperty(
		name="Max Retries",
		description="Maximum number of retry attempts for failed imports",
		default=1,
		min=0,
		max=5
	) # type: ignore

	clear_cache_between_folders: BoolProperty(
		name="Clear Cache Between Folders",
		description="Clear texture cache when moving to next folder",
		default=True
	) # type: ignore

	# Emission Settings (when using emissive template)

	emission_strength: FloatProperty(
		name="Emission Strength",
		description="Strength of emission shader for thumbnails",
		default=1.0,
		min=0.0,
		max=10.0
	) # type: ignore

	emission_factor: FloatProperty(
		name="Emission Mix Factor",
		description="How much emission to mix with base material",
		default=0.25,
		min=0.0,
		max=1.0
	) # type: ignore

	# Extras

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

	# Preview and Validation

	validate_textures: BoolProperty(
		name="Validate Textures",
		description="Validate texture files before processing",
		default=True
	) # type: ignore

	show_processing_log: BoolProperty(
		name="Show Processing Log",
		description="Display detailed processing log in console",
		default=False
	) # type: ignore

	thorough_scene_clear: BoolProperty(
		name="Thorough Scene Clear",
		description="Use comprehensive scene clearing between files (recommended for clean results)",
		default=True
	) # type: ignore

	# Export Options

	embed_textures: BoolProperty(
		name="Embed Textures in GLB",
		description="Include texture images inside the GLB file (larger file size but self-contained)",
		default=False
	) # type: ignore

	export_format: EnumProperty(
		name="Export Format",
		description="Choose export format",
		items=[
			('GLB', 'GLB (Binary)', 'Export as single binary GLB file'),
			('GLTF_SEPARATE', 'GLTF + Textures', 'Export as GLTF with separate texture files'),
		],
		default='GLB'
	) # type: ignore

	use_legacy_materials: BoolProperty(
		name="Use Legacy Material System",
		description="Use the original material system if new system has issues",
		default=False
	) # type: ignore


