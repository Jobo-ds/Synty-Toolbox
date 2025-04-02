import bpy
import os

def export_as_glb(original_fbx_path, output_folder):
	try:
		base_name = os.path.splitext(os.path.basename(original_fbx_path))[0]

		scale_flags = bpy.context.scene.get('scale_flags', [])
		if scale_flags:
			suffix = "_scaled"
			if "upscaled" in scale_flags and "downscaled" not in scale_flags:
				suffix = "_upscaled"
			elif "downscaled" in scale_flags and "upscaled" not in scale_flags:
				suffix = "_downscaled"
			base_name += suffix

		output_path = os.path.join(output_folder, base_name + ".glb")

		bpy.ops.export_scene.gltf(
			filepath=output_path,
			export_format='GLB',
			export_apply=True,
			export_materials='EXPORT',
			use_selection=False
		)

		print(f"[INFO] Exported GLB: {output_path}")
		return output_path

	except Exception as e:
		print(f"[ERROR] Failed to export {original_fbx_path} as GLB: {e}")
		return None
