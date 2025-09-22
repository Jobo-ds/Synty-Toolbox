import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, FloatProperty
from bpy.types import PropertyGroup

class SSTOOL_PG_GLB2BlendProperties(PropertyGroup):
	# Input/Output
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

	# Import Options
	import_materials: EnumProperty(
		name="Materials",
		description="How to handle materials during import",
		items=[
			('IMPORT', 'Import All', 'Import all materials from GLB'),
			('NONE', 'Skip Materials', 'Import geometry only, no materials'),
			('PLACEHOLDER', 'Placeholder Materials', 'Create simple placeholder materials')
		],
		default='IMPORT'
	) # type: ignore

	import_animations: BoolProperty(
		name="Import Animations",
		description="Import animations from GLB files",
		default=True
	) # type: ignore

	import_cameras: BoolProperty(
		name="Import Cameras",
		description="Import cameras from GLB files",
		default=False
	) # type: ignore

	import_lights: BoolProperty(
		name="Import Lights",
		description="Import lights from GLB files",
		default=False
	) # type: ignore

	# Organization Options
	organize_collections: BoolProperty(
		name="Organize in Collections",
		description="Create collections for each GLB file",
		default=True
	) # type: ignore

	collection_naming: EnumProperty(
		name="Collection Naming",
		description="How to name collections",
		items=[
			('FILENAME', 'File Name', 'Use GLB filename for collection'),
			('FOLDER', 'Folder Name', 'Use parent folder name'),
			('CUSTOM', 'Custom Pattern', 'Use custom naming pattern')
		],
		default='FILENAME'
	) # type: ignore

	custom_collection_pattern: StringProperty(
		name="Collection Pattern",
		description="Custom pattern for collection names (use {filename}, {folder})",
		default="{filename}_imported"
	) # type: ignore

	# Output Options
	output_mode: EnumProperty(
		name="Output Mode",
		description="How to organize output files",
		items=[
			('INDIVIDUAL', 'Individual Files', 'One .blend file per GLB'),
			('MERGE_FOLDER', 'Merge by Folder', 'Combine GLBs from same folder into one .blend'),
			('MERGE_ALL', 'Single File', 'Combine all GLBs into one .blend file')
		],
		default='INDIVIDUAL'
	) # type: ignore

	# Naming Options
	use_col_suffix: BoolProperty(
		name="Add '-col' suffix",
		description="Add '-col' suffix to all object names",
		default=False
	) # type: ignore

	custom_object_suffix: StringProperty(
		name="Custom Object Suffix",
		description="Custom suffix to add to object names",
		default=""
	) # type: ignore

	preserve_hierarchy: BoolProperty(
		name="Preserve Hierarchy",
		description="Maintain parent-child relationships from GLB",
		default=True
	) # type: ignore

	# Processing Options
	continue_on_error: BoolProperty(
		name="Continue on Error",
		description="Continue processing if individual files fail",
		default=True
	) # type: ignore

	validate_glb_files: BoolProperty(
		name="Validate GLB Files",
		description="Check GLB file integrity before import",
		default=False
	) # type: ignore

	clear_scene_between: BoolProperty(
		name="Clear Scene Between Files",
		description="Clear scene between each GLB import (recommended)",
		default=True
	) # type: ignore

	# Performance Options
	memory_limit_mb: IntProperty(
		name="Memory Limit (MB)",
		description="Clear memory when usage exceeds this limit",
		default=1024,
		min=256,
		max=8192
	) # type: ignore

	batch_size: IntProperty(
		name="Batch Size",
		description="Number of files to process before memory cleanup",
		default=10,
		min=1,
		max=100
	) # type: ignore

	# Scale Options
	apply_scale: BoolProperty(
		name="Apply Scale",
		description="Apply object transforms on import",
		default=False
	) # type: ignore

	uniform_scale: FloatProperty(
		name="Uniform Scale",
		description="Apply uniform scaling to all imported objects",
		default=1.0,
		min=0.001,
		max=1000.0
	) # type: ignore

	# Advanced Options
	show_processing_log: BoolProperty(
		name="Show Detailed Log",
		description="Display detailed processing information",
		default=True
	) # type: ignore

	backup_existing: BoolProperty(
		name="Backup Existing Files",
		description="Create backups of existing .blend files before overwriting",
		default=False
	) # type: ignore
