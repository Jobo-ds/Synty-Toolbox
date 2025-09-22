import bpy
import os

def export_as_glb(original_fbx_path, output_folder):
	"""
	Export scene as GLB/GLTF with configurable texture handling.

	Supports both embedded textures (larger files) and separate texture files
	based on user preferences.
	"""
	try:
		# Get export settings from scene properties
		props = bpy.context.scene.fbx2glb_props
		embed_textures = getattr(props, 'embed_textures', False)
		export_format = getattr(props, 'export_format', 'GLB')

		base_name = os.path.splitext(os.path.basename(original_fbx_path))[0]

		# Handle scale suffixes
		scale_flags = bpy.context.scene.get('scale_flags', [])
		if scale_flags:
			suffix = "_scaled"
			if "upscaled" in scale_flags and "downscaled" not in scale_flags:
				suffix = "_upscaled"
			elif "downscaled" in scale_flags and "upscaled" not in scale_flags:
				suffix = "_downscaled"
			base_name += suffix

		# Determine output format and path
		if export_format == 'GLTF_SEPARATE':
			output_path = os.path.join(output_folder, base_name + ".gltf")
			export_format_setting = 'GLTF_SEPARATE'
		else:
			output_path = os.path.join(output_folder, base_name + ".glb")
			export_format_setting = 'GLB'

		# Configure export parameters
		export_params = {
			'filepath': output_path,
			'export_format': export_format_setting,
			'export_apply': True,
			'export_materials': 'EXPORT',
			'use_selection': False,
			'export_texcoords': True,
			'export_normals': True,
			'export_tangents': False,
			'export_colors': True
		}

		# Configure texture settings
		if export_format_setting == 'GLB':
			# For GLB, control texture embedding
			if embed_textures:
				export_params['export_image_format'] = 'AUTO'  # Embed images
				export_params['export_texture_dir'] = ''
				print(f"[INFO] Exporting GLB with embedded textures: {output_path}")
			else:
				# GLB without embedded textures - use external texture references
				export_params['export_image_format'] = 'JPEG'  # Don't embed, reference external
				export_params['export_texture_dir'] = output_folder
				print(f"[INFO] Exporting GLB with external texture references: {output_path}")
		else:
			# For GLTF_SEPARATE, always use separate texture files
			export_params['export_image_format'] = 'JPEG'
			export_params['export_texture_dir'] = output_folder
			print(f"[INFO] Exporting GLTF with separate texture files: {output_path}")

		# Perform the export
		bpy.ops.export_scene.gltf(**export_params)

		return output_path

	except Exception as e:
		print(f"[ERROR] Failed to export {original_fbx_path}: {e}")
		return None
