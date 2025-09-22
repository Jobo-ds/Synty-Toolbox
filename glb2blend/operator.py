import bpy
from bpy.types import Operator
import pathlib
import os
import shutil
import gc
import time
from ..utils.blender import clear_scene
from ..utils.memory import purge_unused_data


def validate_glb_file(filepath):
	"""Validate GLB file integrity - basic check only"""
	try:
		if not os.path.exists(filepath):
			return False, "File does not exist"

		if os.path.getsize(filepath) < 20:  # GLB header is 20 bytes minimum
			return False, "File too small to be valid GLB"

		# Check if it has .glb extension (simple check)
		if not filepath.lower().endswith('.glb'):
			return False, "Not a GLB file"

		# Basic header check - but be more lenient
		try:
			with open(filepath, 'rb') as f:
				header = f.read(4)
				if header != b'glTF':
					# Try GLTF format as well
					if not header.startswith(b'{'):
						return False, "Invalid GLB/GLTF header"
		except:
			# If we can't read the header, just warn but don't fail
			print(f"[WARNING] Could not read header of {filepath}, will try import anyway")

		return True, "Valid GLB file"
	except Exception as e:
		print(f"[WARNING] Validation error for {filepath}: {e}")
		return True, f"Validation warning: {e}"  # Don't fail on validation errors


def create_collection(name, parent=None):
	"""Create a new collection with the given name"""
	collection = bpy.data.collections.new(name)
	if parent:
		parent.children.link(collection)
	else:
		bpy.context.scene.collection.children.link(collection)
	return collection


def organize_objects_in_collection(collection_name, imported_objects):
	"""Move imported objects to a specific collection"""
	try:
		collection = create_collection(collection_name)

		for obj in imported_objects:
			# Remove from all other collections
			for col in obj.users_collection:
				col.objects.unlink(obj)
			# Add to our collection
			collection.objects.link(obj)

		return collection
	except Exception as e:
		print(f"[ERROR] Failed to organize collection: {e}")
		return None


def apply_object_naming(objects, props):
	"""Apply naming conventions to objects"""
	try:
		suffix = ""
		if props.use_col_suffix:
			suffix = "-col"
		elif props.custom_object_suffix:
			suffix = props.custom_object_suffix

		if suffix:
			for obj in objects:
				if not obj.name.endswith(suffix):
					obj.name = f"{obj.name}{suffix}"
				if hasattr(obj.data, "name") and obj.data and not obj.data.name.endswith(suffix):
					obj.data.name = f"{obj.data.name}{suffix}"
	except Exception as e:
		print(f"[ERROR] Failed to apply naming: {e}")


def apply_material_handling(objects, props):
	"""Handle material processing based on settings"""
	try:
		if props.import_materials == 'NONE':
			# Remove all materials
			for obj in objects:
				if obj.type == 'MESH' and obj.data.materials:
					obj.data.materials.clear()

		elif props.import_materials == 'PLACEHOLDER':
			# Create simple placeholder materials
			placeholder_mat = bpy.data.materials.get("GLB_Placeholder")
			if not placeholder_mat:
				placeholder_mat = bpy.data.materials.new("GLB_Placeholder")
				placeholder_mat.use_nodes = True
				# Make it a simple gray material
				if placeholder_mat.node_tree:
					bsdf = placeholder_mat.node_tree.nodes.get("Principled BSDF")
					if bsdf:
						bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)

			for obj in objects:
				if obj.type == 'MESH':
					obj.data.materials.clear()
					obj.data.materials.append(placeholder_mat)

	except Exception as e:
		print(f"[ERROR] Failed to handle materials: {e}")


def apply_scaling(objects, props):
	"""Apply scaling to imported objects"""
	try:
		if props.uniform_scale != 1.0:
			for obj in objects:
				obj.scale = (props.uniform_scale, props.uniform_scale, props.uniform_scale)
				if props.apply_scale:
					# Apply the scale to mesh data
					bpy.context.view_layer.objects.active = obj
					obj.select_set(True)
					try:
						bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
					except:
						pass
					finally:
						obj.select_set(False)
	except Exception as e:
		print(f"[ERROR] Failed to apply scaling: {e}")


def backup_existing_file(filepath):
	"""Create backup of existing blend file"""
	try:
		if os.path.exists(filepath):
			backup_path = filepath + ".backup"
			shutil.copy2(filepath, backup_path)
			return backup_path
		return None
	except Exception as e:
		print(f"[ERROR] Failed to create backup: {e}")
		return None


def get_collection_name(glb_path, input_dir, props):
	"""Generate collection name based on settings"""
	try:
		filename = glb_path.stem
		folder = glb_path.parent.name

		if props.collection_naming == 'FILENAME':
			return filename
		elif props.collection_naming == 'FOLDER':
			return folder
		elif props.collection_naming == 'CUSTOM':
			pattern = props.custom_collection_pattern
			return pattern.format(filename=filename, folder=folder)
		else:
			return filename
	except Exception as e:
		print(f"[ERROR] Failed to generate collection name: {e}")
		return "GLB_Import"


class SSTOOL_OT_GLB2BlendOperator(Operator):
	bl_idname = "object.convert_glb_to_blend"
	bl_label = "Convert GLB to Blend (Enhanced)"
	bl_description = "Convert GLB files to Blend with advanced options"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		try:
			print("[INFO] Starting GLB to Blend conversion")
			start_time = time.time()

			props = context.scene.glb2blend_props
			input_dir = pathlib.Path(bpy.path.abspath(props.input_dir))
			output_dir = pathlib.Path(bpy.path.abspath(props.output_dir))

			# Validation
			if not input_dir.exists():
				self.report({'ERROR'}, f"Input directory does not exist: {input_dir}")
				return {'CANCELLED'}

			if not output_dir.exists():
				try:
					output_dir.mkdir(parents=True, exist_ok=True)
				except Exception as e:
					self.report({'ERROR'}, f"Cannot create output directory: {e}")
					return {'CANCELLED'}

			# Find all GLB files
			glb_files = list(input_dir.rglob("*.glb"))
			if not glb_files:
				self.report({'WARNING'}, "No GLB files found in input directory")
				return {'CANCELLED'}

			print(f"[INFO] Found {len(glb_files)} GLB files")

			# Process files based on output mode
			if props.output_mode == 'INDIVIDUAL':
				return self._process_individual_files(glb_files, input_dir, output_dir, props)
			elif props.output_mode == 'MERGE_FOLDER':
				return self._process_merged_by_folder(glb_files, input_dir, output_dir, props)
			elif props.output_mode == 'MERGE_ALL':
				return self._process_single_file(glb_files, input_dir, output_dir, props)

		except Exception as e:
			error_msg = f"Processing failed: {e}"
			print(f"[ERROR] {error_msg}")
			import traceback
			traceback.print_exc()
			self.report({'ERROR'}, error_msg)
			return {'CANCELLED'}

	def _process_individual_files(self, glb_files, input_dir, output_dir, props):
		"""Process each GLB file into individual blend files"""
		total_processed = 0
		total_failed = 0
		processed_count = 0

		for glb_path in glb_files:
			try:
				print(f"[DEBUG] Starting processing: {glb_path}")

				# Validate GLB file
				if props.validate_glb_files:
					print(f"[DEBUG] Validating {glb_path.name}")
					valid, msg = validate_glb_file(str(glb_path))
					if not valid:
						print(f"[ERROR] Invalid GLB file {glb_path.name}: {msg}")
						if props.continue_on_error:
							total_failed += 1
							continue
						else:
							self.report({'ERROR'}, f"Invalid GLB file: {msg}")
							return {'CANCELLED'}

				# Clear scene if requested
				if props.clear_scene_between:
					print(f"[DEBUG] Clearing scene before import")
					clear_scene()

				# Store objects before import to identify new ones
				objects_before = set(bpy.data.objects)
				print(f"[DEBUG] Objects before import: {len(objects_before)}")

				# Import GLB with settings
				print(f"[DEBUG] Importing GLB: {glb_path}")
				self._import_glb_with_settings(str(glb_path), props)

				# Get newly imported objects
				imported_objects = list(set(bpy.data.objects) - objects_before)
				print(f"[DEBUG] Objects imported: {len(imported_objects)}")

				if not imported_objects:
					print(f"[WARNING] No objects imported from {glb_path.name}")
					if props.continue_on_error:
						total_failed += 1
						continue
					else:
						return {'CANCELLED'}

				# Process imported objects
				self._process_imported_objects(imported_objects, glb_path, input_dir, props)

				# Determine output path
				rel_path = glb_path.relative_to(input_dir).with_suffix("")
				output_blend_path = output_dir / rel_path.with_suffix(".blend")
				output_blend_path.parent.mkdir(parents=True, exist_ok=True)

				# Backup existing file if requested
				if props.backup_existing:
					backup_existing_file(str(output_blend_path))

				# Save blend file
				bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path))
				total_processed += 1

				if props.show_processing_log:
					print(f"[INFO] Saved: {output_blend_path.name}")

				# Memory management
				processed_count += 1
				if processed_count % props.batch_size == 0:
					if props.show_processing_log:
						print("[INFO] Performing memory cleanup")
					purge_unused_data()
					gc.collect()

			except Exception as e:
				total_failed += 1
				print(f"[ERROR] Failed to process {glb_path.name}: {e}")
				if not props.continue_on_error:
					self.report({'ERROR'}, f"Processing failed: {e}")
					return {'CANCELLED'}

		# Final cleanup
		clear_scene()
		purge_unused_data()

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

	def _process_merged_by_folder(self, glb_files, input_dir, output_dir, props):
		"""Process GLB files merged by folder"""
		# Group files by folder
		folders = {}
		for glb_path in glb_files:
			folder_key = glb_path.parent
			if folder_key not in folders:
				folders[folder_key] = []
			folders[folder_key].append(glb_path)

		total_processed = 0
		total_failed = 0

		for folder, files in folders.items():
			try:
				if props.show_processing_log:
					print(f"[INFO] Processing folder: {folder.name} ({len(files)} files)")

				if props.clear_scene_between:
					clear_scene()

				# Import all GLB files from this folder
				all_imported_objects = []
				for glb_path in files:
					try:
						if props.validate_glb_files:
							valid, msg = validate_glb_file(str(glb_path))
							if not valid:
								print(f"[ERROR] Invalid GLB file {glb_path.name}: {msg}")
								continue

						objects_before = set(bpy.data.objects)
						self._import_glb_with_settings(str(glb_path), props)
						imported_objects = list(set(bpy.data.objects) - objects_before)

						if imported_objects:
							# Organize in collection per file
							if props.organize_collections:
								collection_name = get_collection_name(glb_path, input_dir, props)
								organize_objects_in_collection(collection_name, imported_objects)

							all_imported_objects.extend(imported_objects)

					except Exception as e:
						print(f"[ERROR] Failed to import {glb_path.name}: {e}")
						if not props.continue_on_error:
							raise

				if all_imported_objects:
					# Process all imported objects
					for glb_path in files:
						# Get objects that belong to this file (simplified approach)
						file_objects = [obj for obj in all_imported_objects if glb_path.stem in obj.name]
						if file_objects:
							self._process_imported_objects(file_objects, glb_path, input_dir, props)

					# Save merged file
					rel_folder = folder.relative_to(input_dir)
					output_blend_path = output_dir / rel_folder / f"{folder.name}_merged.blend"
					output_blend_path.parent.mkdir(parents=True, exist_ok=True)

					if props.backup_existing:
						backup_existing_file(str(output_blend_path))

					bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path))
					total_processed += len(files)

					if props.show_processing_log:
						print(f"[INFO] Saved merged file: {output_blend_path.name}")

			except Exception as e:
				total_failed += len(files)
				print(f"[ERROR] Failed to process folder {folder.name}: {e}")
				if not props.continue_on_error:
					self.report({'ERROR'}, f"Processing failed: {e}")
					return {'CANCELLED'}

		# Final cleanup
		clear_scene()
		purge_unused_data()

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

	def _process_single_file(self, glb_files, input_dir, output_dir, props):
		"""Process all GLB files into a single blend file"""
		try:
			if props.show_processing_log:
				print(f"[INFO] Processing all {len(glb_files)} files into single blend")

			clear_scene()
			total_processed = 0
			total_failed = 0

			for glb_path in glb_files:
				try:
					if props.validate_glb_files:
						valid, msg = validate_glb_file(str(glb_path))
						if not valid:
							print(f"[ERROR] Invalid GLB file {glb_path.name}: {msg}")
							if props.continue_on_error:
								total_failed += 1
								continue
							else:
								raise Exception(msg)

					objects_before = set(bpy.data.objects)
					self._import_glb_with_settings(str(glb_path), props)
					imported_objects = list(set(bpy.data.objects) - objects_before)

					if imported_objects:
						# Organize in collection per file
						if props.organize_collections:
							collection_name = get_collection_name(glb_path, input_dir, props)
							organize_objects_in_collection(collection_name, imported_objects)

						self._process_imported_objects(imported_objects, glb_path, input_dir, props)
						total_processed += 1

						if props.show_processing_log:
							print(f"[INFO] Imported: {glb_path.name}")

				except Exception as e:
					total_failed += 1
					print(f"[ERROR] Failed to import {glb_path.name}: {e}")
					if not props.continue_on_error:
						raise

			# Save single merged file
			output_blend_path = output_dir / "all_glb_merged.blend"
			if props.backup_existing:
				backup_existing_file(str(output_blend_path))

			bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path))

			if props.show_processing_log:
				print(f"[INFO] Saved merged file: {output_blend_path.name}")

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
			error_msg = f"Single file processing failed: {e}"
			print(f"[ERROR] {error_msg}")
			self.report({'ERROR'}, error_msg)
			return {'CANCELLED'}

	def _import_glb_with_settings(self, filepath, props):
		"""Import GLB file with the specified settings"""
		try:
			# Use basic import parameters that are known to work
			import_params = {
				'filepath': filepath
			}

			# Only add parameters that we're confident about
			if hasattr(bpy.ops.import_scene.gltf, '__annotations__'):
				# Add safe parameters
				if not props.import_animations:
					import_params['import_animations'] = False

				# Use basic material import
				if props.import_materials == 'NONE':
					import_params['import_shading'] = 'FLAT'

			if props.show_processing_log:
				print(f"[DEBUG] Importing GLB with params: {import_params}")

			bpy.ops.import_scene.gltf(**import_params)

		except Exception as e:
			print(f"[ERROR] GLB import failed: {e}")
			# Try with minimal parameters as fallback
			try:
				print("[DEBUG] Attempting basic GLB import...")
				bpy.ops.import_scene.gltf(filepath=filepath)
			except Exception as e2:
				print(f"[ERROR] Basic GLB import also failed: {e2}")
				raise e2

	def _process_imported_objects(self, imported_objects, glb_path, input_dir, props):
		"""Process imported objects with all the settings"""
		try:
			# Apply naming conventions
			apply_object_naming(imported_objects, props)

			# Handle materials
			apply_material_handling(imported_objects, props)

			# Apply scaling
			apply_scaling(imported_objects, props)

		except Exception as e:
			print(f"[ERROR] Failed to process objects from {glb_path.name}: {e}")


class SSTOOL_OT_TestGLB2BlendOperator(Operator):
	bl_idname = "object.test_glb2blend_converter"
	bl_label = "Test GLB to Blend (Simple)"
	bl_description = "Simple test version of GLB to Blend converter"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		"""Simple test version using basic approach"""
		try:
			print("[TEST] Starting simple GLB to Blend test")

			# Get basic settings
			props = context.scene.glb2blend_props
			input_dir = props.input_dir

			if not input_dir:
				self.report({'ERROR'}, "No input directory specified")
				return {'CANCELLED'}

			print(f"[TEST] Input directory: {input_dir}")

			# Get one GLB file to test
			glb_files = []
			import pathlib
			input_path = pathlib.Path(bpy.path.abspath(input_dir))

			if not input_path.exists():
				self.report({'ERROR'}, "Input directory does not exist")
				return {'CANCELLED'}

			for glb_file in input_path.rglob("*.glb"):
				glb_files.append(glb_file)
				break  # Just take the first one for testing

			if not glb_files:
				self.report({'ERROR'}, "No GLB files found")
				return {'CANCELLED'}

			glb_file = glb_files[0]
			print(f"[TEST] Processing: {glb_file}")

			# Clear scene using simple method
			print("[TEST] Clearing scene")
			clear_scene()

			# Import GLB
			print("[TEST] Importing GLB")
			bpy.ops.import_scene.gltf(filepath=str(glb_file))

			# Apply basic naming if requested
			if props.use_col_suffix:
				print("[TEST] Adding -col suffix")
				for obj in bpy.data.objects:
					if not obj.name.endswith("-col"):
						obj.name = f"{obj.name}-col"

			# Save test file
			print("[TEST] Saving test file")
			output_dir = pathlib.Path(bpy.path.abspath(props.output_dir))
			if not output_dir.exists():
				output_dir.mkdir(parents=True, exist_ok=True)

			test_output = output_dir / f"{glb_file.stem}_test.blend"
			bpy.ops.wm.save_as_mainfile(filepath=str(test_output))

			print(f"[TEST] Success! Saved: {test_output}")
			self.report({'INFO'}, f"Test successful: {test_output}")
			return {'FINISHED'}

		except Exception as e:
			print(f"[TEST] Error: {e}")
			import traceback
			traceback.print_exc()
			self.report({'ERROR'}, f"Test failed: {e}")
			return {'CANCELLED'}
