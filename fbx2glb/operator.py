import bpy
import os
from bpy.types import Operator


def simple_clear_scene():
	"""Simple scene clearing that always works"""
	try:
		# Select all objects
		bpy.ops.object.select_all(action='SELECT')
		# Delete all objects
		bpy.ops.object.delete(use_global=False)

		# Clear materials
		for material in list(bpy.data.materials):
			if material.users == 0:
				bpy.data.materials.remove(material)

		# Clear meshes
		for mesh in list(bpy.data.meshes):
			if mesh.users == 0:
				bpy.data.meshes.remove(mesh)

		print("[INFO] Scene cleared")
	except Exception as e:
		print(f"[WARNING] Scene clear error: {e}")


def replace_materials_with_texture(texture_path=None):
	"""Replace all existing materials with simple texture-only materials"""
	try:
		if not texture_path or not os.path.exists(texture_path):
			print("[INFO] No texture provided, keeping materials as-is")
			return

		print(f"[INFO] Replacing materials with texture: {os.path.basename(texture_path)}")

		# Get all existing materials in the scene
		existing_materials = list(bpy.data.materials)

		for original_mat in existing_materials:
			if original_mat.users == 0:
				continue  # Skip unused materials

			# Create new simple material with same name
			new_mat = bpy.data.materials.new(name=original_mat.name + "_textured")
			new_mat.use_nodes = True

			# Clear default nodes
			nodes = new_mat.node_tree.nodes
			nodes.clear()

			# Add Principled BSDF
			bsdf = nodes.new("ShaderNodeBsdfPrincipled")
			bsdf.location = (0, 0)

			# Add Material Output
			output = nodes.new("ShaderNodeOutputMaterial")
			output.location = (300, 0)

			# Connect BSDF to output
			new_mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

			# Add texture
			tex_node = nodes.new("ShaderNodeTexImage")
			tex_node.image = bpy.data.images.load(texture_path, check_existing=True)
			tex_node.location = (-300, 0)
			new_mat.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

			# Simple material settings - no alpha
			new_mat.blend_method = 'OPAQUE'

			# Replace the material on all objects that use it
			for obj in bpy.data.objects:
				if obj.type == 'MESH' and obj.data.materials:
					for i, mat_slot in enumerate(obj.data.materials):
						if mat_slot == original_mat:
							obj.data.materials[i] = new_mat

			# Remove the original material
			bpy.data.materials.remove(original_mat)

		print(f"[INFO] Replaced {len(existing_materials)} materials with textured versions")

	except Exception as e:
		print(f"[ERROR] Material replacement failed: {e}")


def normalize_object_scales():
	"""Set all object scales directly to 1.0 if they're not already 1.0"""
	try:
		normalized_count = 0
		for obj in bpy.context.scene.objects:
			# Check if scale is not (1.0, 1.0, 1.0)
			if abs(obj.scale.x - 1.0) > 0.001 or abs(obj.scale.y - 1.0) > 0.001 or abs(obj.scale.z - 1.0) > 0.001:
				old_scale = obj.scale.copy()
				print(f"[INFO] Changing scale for {obj.name}: {old_scale} -> (1.0, 1.0, 1.0)")

				# Directly set scale to 1.0
				obj.scale = (1.0, 1.0, 1.0)
				normalized_count += 1

		if normalized_count > 0:
			print(f"[INFO] Changed scale on {normalized_count} objects")
		else:
			print("[INFO] All objects already have scale 1.0")

	except Exception as e:
		print(f"[ERROR] Scale normalization failed: {e}")


class SSTOOL_OT_FBX2GLBOperator(Operator):
	bl_idname = "sstool.fbx2glb_converter"
	bl_label = "Process FBX Files"
	bl_description = "Imports FBX files, creates fresh materials, and exports as GLB"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		"""Execute the FBX to GLB conversion using simplified approach"""
		try:
			print("[INFO] Starting FBX to GLB conversion")

			# Get settings
			props = context.scene.fbx2glb_props
			input_folder = props.fbx_folder

			if not input_folder:
				self.report({'ERROR'}, "No input folder specified")
				return {'CANCELLED'}

			print(f"[INFO] Input folder: {input_folder}")

			# Get folders to process
			folders_to_process = []
			if props.search_subfolders:
				# Simple subfolder search
				for root, dirs, files in os.walk(input_folder):
					if any(f.lower().endswith('.fbx') for f in files):
						folders_to_process.append(root)
			else:
				folders_to_process.append(input_folder)

			print(f"[INFO] Processing {len(folders_to_process)} folders")

			total_processed = 0
			total_failed = 0

			# Process each folder
			for folder in folders_to_process:
				print(f"[INFO] Processing folder: {folder}")

				# Auto-detect texture (no normal maps)
				texture_file = ""

				if props.auto_find_texture:
					try:
						for filename in os.listdir(folder):
							if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
								# Skip files with 'normal' in the name
								if 'normal' not in filename.lower():
									texture_file = os.path.join(folder, filename)
									print(f"[INFO] Found texture: {filename}")
									break  # Use first non-normal texture found
					except Exception as e:
						print(f"[WARNING] Error scanning for textures: {e}")

				# Use manually specified texture if not auto-detecting
				if not props.auto_find_texture and props.texture_file:
					texture_file = props.texture_file

				# Setup output folder
				if props.output_root_folder:
					relative_path = os.path.relpath(folder, input_folder)
					output_folder = os.path.join(props.output_root_folder, relative_path)
					os.makedirs(output_folder, exist_ok=True)
				else:
					# Create output folder in the same directory
					output_folder = os.path.join(folder, "output")
					os.makedirs(output_folder, exist_ok=True)

				# Get FBX files
				fbx_files = []
				try:
					for filename in os.listdir(folder):
						if filename.lower().endswith('.fbx'):
							fbx_files.append(os.path.join(folder, filename))
				except Exception as e:
					print(f"[ERROR] Cannot list files in {folder}: {e}")
					continue

				if not fbx_files:
					print(f"[WARNING] No FBX files found in {folder}")
					continue

				print(f"[INFO] Found {len(fbx_files)} FBX files")

				# Process each FBX file
				for fbx_file in fbx_files:
					try:
						filename = os.path.basename(fbx_file)
						print(f"[INFO] Processing: {filename}")

						# Clear scene
						simple_clear_scene()

						# Import FBX
						print(f"[INFO] Importing FBX: {filename}")
						bpy.ops.import_scene.fbx(filepath=fbx_file)

						# Normalize object scales if enabled
						if props.reset_object_scale:
							print("[INFO] Normalizing object scales")
							normalize_object_scales()

						# Replace all materials with simple textured materials
						print("[INFO] Replacing materials with texture")
						replace_materials_with_texture(texture_file)

						# Export GLB
						print(f"[INFO] Exporting GLB: {filename}")
						base_name = os.path.splitext(filename)[0]
						export_path = os.path.join(output_folder, base_name + ".glb")

						# Simple GLB export
						bpy.ops.export_scene.gltf(
							filepath=export_path,
							export_format='GLB',
							export_apply=True,
							export_materials='EXPORT',
							use_selection=False
						)

						if os.path.exists(export_path):
							total_processed += 1
							print(f"[INFO] Successfully exported: {filename}")
						else:
							total_failed += 1
							print(f"[ERROR] Export failed: {filename}")

					except Exception as e:
						total_failed += 1
						print(f"[ERROR] Failed to process {filename}: {e}")
						import traceback
						traceback.print_exc()
						continue

			# Final cleanup
			simple_clear_scene()

			# Report results
			if total_processed > 0:
				if total_failed > 0:
					self.report({'WARNING'}, f"Processed {total_processed} files, {total_failed} failed")
				else:
					self.report({'INFO'}, f"Successfully processed all {total_processed} files")
				return {'FINISHED'}
			else:
				self.report({'ERROR'}, f"All {total_failed} files failed to process")
				return {'CANCELLED'}

		except Exception as e:
			error_msg = f"Processing failed: {e}"
			print(f"[ERROR] {error_msg}")
			import traceback
			traceback.print_exc()
			self.report({'ERROR'}, error_msg)
			return {'CANCELLED'}

