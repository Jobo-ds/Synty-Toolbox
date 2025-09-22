import os
import bpy
from typing import List, Dict, Optional, Callable
from ...utils.logging import BatchProcessor, ProcessingResult
from ...utils.file_detection import FileValidator, TextureDetector
from ...utils.texture_cache import texture_cache
from ...utils.blender import clear_scene, force_clear_scene
from ...utils.memory import purge_unused_data
from ...utils.folder_operations import create_output_folder, get_subfolders
from ..materials.material_factory import material_factory
from ..importers.fbx import import_fbx
from ..exporters.glb import export_as_glb
from ..utils.corrections import rotate_armatures, normalize_object_group_scale
from ..utils.clean_up import remove_import_clutter
from ...simplifymat.operator import merge_duplicate_materials

class ProcessingSettings:
    """Configuration for FBX to GLB processing"""
    def __init__(self, props=None):
        print(f"[DEBUG] ProcessingSettings init with props: {props}")

        # Input/Output settings
        try:
            self.input_folder = props.fbx_folder if props else ""
            print(f"[DEBUG] Input folder: {self.input_folder}")
        except Exception as e:
            print(f"[ERROR] Failed to get fbx_folder: {e}")
            self.input_folder = ""

        try:
            self.output_folder = props.output_root_folder if props else ""
            print(f"[DEBUG] Output folder: {self.output_folder}")
        except Exception as e:
            print(f"[ERROR] Failed to get output_root_folder: {e}")
            self.output_folder = ""

        try:
            self.search_subfolders = props.search_subfolders if props else False
            print(f"[DEBUG] Search subfolders: {self.search_subfolders}")
        except Exception as e:
            print(f"[ERROR] Failed to get search_subfolders: {e}")
            self.search_subfolders = False

        # Material settings
        self.material_template = getattr(props, 'material_template', 'standard')
        self.inherit_material_values = props.inherit_material_values if props else True
        self.force_texture = props.force_texture if props else False
        self.use_emission = props.use_emission if props else True
        self.use_error_material = props.use_error_material if props else True

        # Mesh settings
        self.character_rotate_fix = props.character_rotate_fix if props else False
        self.auto_normalize_scale = props.auto_normalize_scale if props else True
        self.remove_clutter = props.remove_clutter if props else True

        # Error handling
        self.continue_on_error = getattr(props, 'continue_on_error', True)
        self.retry_failed_imports = getattr(props, 'retry_failed_imports', True)
        self.max_retries = getattr(props, 'max_retries', 1)

        # Performance
        self.clear_cache_between_folders = getattr(props, 'clear_cache_between_folders', True)
        self.thorough_scene_clear = getattr(props, 'thorough_scene_clear', True)

        # Export settings
        self.embed_textures = getattr(props, 'embed_textures', False)
        self.export_format = getattr(props, 'export_format', 'GLB')
        self.use_legacy_materials = getattr(props, 'use_legacy_materials', False)

class FBXProcessingService:
    """Service for processing FBX files to GLB with enhanced error handling and performance"""

    def __init__(self, settings: ProcessingSettings, progress_callback: Optional[Callable] = None):
        self.settings = settings
        self.progress_callback = progress_callback
        self.batch_processor = BatchProcessor(continue_on_error=settings.continue_on_error)

        # Reset material counter for consistent naming
        material_factory.reset_counter()

        print("[INFO] FBX Processing Service initialized")

    def process_batch(self) -> Dict:
        """Process all FBX files according to settings"""
        print("[INFO] Starting batch processing")

        try:
            # Get folders to process
            folders_to_process = self._get_folders_to_process()
            if not folders_to_process:
                result = ProcessingResult(False, "No folders found to process")
                self.batch_processor.add_result(result)
                return self.batch_processor.get_summary()

            total_folders = len(folders_to_process)
            print(f"[INFO] Processing {total_folders} folders")

            # Process each folder
            for i, folder_path in enumerate(folders_to_process):
                if self.progress_callback:
                    self.progress_callback(i / total_folders, f"Processing folder {i+1}/{total_folders}")

                self._process_folder(folder_path)

                # Clear cache between folders if requested
                if self.settings.clear_cache_between_folders:
                    texture_cache.clear_cache()

            # Final cleanup
            if self.settings.thorough_scene_clear:
                clear_scene()
            else:
                from ...utils.blender import clear_scene_legacy
                clear_scene_legacy()
            purge_unused_data()

            summary = self.batch_processor.get_summary()
            print(f"[INFO] Batch processing complete: {summary['successful']}/{summary['total_processed']} successful")

            return summary

        except Exception as e:
            print(f"[ERROR] Batch processing failed: {e}")
            result = ProcessingResult(False, f"Batch processing error: {e}")
            self.batch_processor.add_result(result)
            return self.batch_processor.get_summary()

    def _get_folders_to_process(self) -> List[str]:
        """Get list of folders to process"""
        folders = []

        if not os.path.exists(self.settings.input_folder):
            print(f"[ERROR] Input folder does not exist: {self.settings.input_folder}")
            return folders

        if self.settings.search_subfolders:
            subfolders = get_subfolders(self.settings.input_folder, "fbx")
            folders.extend(subfolders)
        else:
            folders.append(self.settings.input_folder)

        print(f"[DEBUG] Found {len(folders)} folders to process")
        return folders

    def _process_folder(self, folder_path: str) -> bool:
        """Process all FBX files in a single folder"""
        print(f"[INFO] Processing folder: {folder_path}")

        try:
            # Get and validate FBX files
            files_with_validation = FileValidator.get_files_with_validation(folder_path, "fbx")
            if not files_with_validation:
                print(f"[WARNING] No FBX files found in {folder_path}")
                return True

            # Setup output folder
            output_folder = self._setup_output_folder(folder_path)
            if not output_folder:
                print(f"[ERROR] Failed to setup output folder for {folder_path}")
                return False

            # Process each FBX file
            for file_path, is_valid, message in files_with_validation:
                if not is_valid:
                    print(f"[WARNING] Skipping invalid file {file_path}: {message}")
                    result = ProcessingResult(False, f"Invalid file: {message}")
                    self.batch_processor.add_result(result, file_path)
                    continue

                success = self._process_single_file(file_path, folder_path, output_folder)
                if not success and not self.settings.continue_on_error:
                    return False

            return True

        except Exception as e:
            print(f"[ERROR] Error processing folder {folder_path}: {e}")
            result = ProcessingResult(False, f"Folder processing error: {e}")
            self.batch_processor.add_result(result, folder_path)
            return False

    def _process_single_file(self, file_path: str, folder_path: str, output_folder: str) -> bool:
        """Process a single FBX file"""
        filename = os.path.basename(file_path)
        print(f"[INFO] Processing file: {filename}")

        retries = 0
        max_retries = self.settings.max_retries if self.settings.retry_failed_imports else 0

        while retries <= max_retries:
            try:
                print(f"[DEBUG] Starting processing attempt {retries + 1} for {filename}")

                # Clear scene before processing
                try:
                    if self.settings.thorough_scene_clear:
                        clear_scene()  # New comprehensive clearing
                    else:
                        # Use legacy clearing for compatibility
                        from ...utils.blender import clear_scene_legacy
                        clear_scene_legacy()
                    print(f"[DEBUG] Scene cleared successfully for {filename}")
                except Exception as e:
                    print(f"[ERROR] Scene clearing failed for {filename}: {e}")
                    # Continue anyway - maybe the scene will still work

                # Import FBX
                print(f"[DEBUG] Starting FBX import for {filename}")
                try:
                    import_success = self._import_fbx_with_retry(file_path)
                    if not import_success:
                        if retries < max_retries:
                            retries += 1
                            print(f"[WARNING] Import failed, retrying ({retries}/{max_retries})")
                            continue
                        else:
                            result = ProcessingResult(False, "Failed to import FBX file")
                            self.batch_processor.add_result(result, file_path)
                            print(f"[ERROR] Final import failure for {filename}")
                            return False
                    print(f"[DEBUG] FBX import successful for {filename}")
                except Exception as e:
                    print(f"[ERROR] FBX import exception for {filename}: {e}")
                    if retries < max_retries:
                        retries += 1
                        continue
                    else:
                        result = ProcessingResult(False, f"Import exception: {e}")
                        self.batch_processor.add_result(result, file_path)
                        return False

                # Process imported objects
                print(f"[DEBUG] Processing imported objects for {filename}")
                try:
                    if self.settings.use_legacy_materials:
                        self._process_imported_objects_legacy(folder_path)
                    else:
                        self._process_imported_objects(folder_path)
                    print(f"[DEBUG] Object processing successful for {filename}")
                except Exception as e:
                    print(f"[ERROR] Object processing failed for {filename}: {e}")
                    # Try legacy materials as fallback
                    if not self.settings.use_legacy_materials:
                        print(f"[INFO] Trying legacy material system for {filename}")
                        try:
                            self._process_imported_objects_legacy(folder_path)
                            print(f"[DEBUG] Legacy object processing successful for {filename}")
                        except Exception as e2:
                            print(f"[ERROR] Legacy object processing also failed for {filename}: {e2}")
                            pass

                # Merge duplicate materials
                print(f"[DEBUG] Merging duplicate materials for {filename}")
                try:
                    if hasattr(bpy.context.scene, 'objects') and bpy.context.scene.objects:
                        merge_duplicate_materials()
                        print(f"[DEBUG] Material merging successful for {filename}")
                except Exception as e:
                    print(f"[WARNING] Material merging failed for {filename}: {e}")
                    # Continue anyway

                # Export as GLB
                print(f"[DEBUG] Starting GLB export for {filename}")
                try:
                    export_path = export_as_glb(file_path, output_folder)
                    if export_path:
                        result = ProcessingResult(True, f"Successfully exported to {export_path}")
                        self.batch_processor.add_result(result, file_path)
                        print(f"[INFO] Successfully processed: {filename}")
                        return True
                    else:
                        result = ProcessingResult(False, "Export function returned None")
                        self.batch_processor.add_result(result, file_path)
                        print(f"[ERROR] Export returned None for {filename}")
                        return False
                except Exception as e:
                    print(f"[ERROR] GLB export exception for {filename}: {e}")
                    result = ProcessingResult(False, f"Export exception: {e}")
                    self.batch_processor.add_result(result, file_path)
                    return False

            except Exception as e:
                if retries < max_retries:
                    retries += 1
                    print(f"[WARNING] Processing failed, retrying ({retries}/{max_retries}) for {filename}: {e}")
                    continue
                else:
                    print(f"[ERROR] Final processing failure for {filename}: {e}")
                    result = ProcessingResult(False, f"Processing error: {e}")
                    self.batch_processor.add_result(result, file_path)
                    return False

        print(f"[ERROR] Exhausted all retries for {filename}")
        return False

    def _import_fbx_with_retry(self, file_path: str) -> bool:
        """Import FBX with error handling"""
        try:
            import_fbx(file_path)
            print(f"[DEBUG] Successfully imported: {file_path}")
            return True
        except RuntimeError as e:
            error_msg = str(e)
            if "ASCII" in error_msg.upper():
                print(f"[ERROR] ASCII FBX import failed: {file_path}")
                # Could potentially implement ASCII FBX conversion here
                return False
            else:
                print(f"[ERROR] FBX import failed: {file_path} - {e}")
                return False
        except Exception as e:
            print(f"[ERROR] Unexpected import error for {file_path}: {e}")
            return False

    def _process_imported_objects(self, folder_path: str):
        """Process all imported objects (materials, corrections, cleanup)"""
        scene_objects = list(bpy.context.scene.objects)

        for obj in scene_objects:
            try:
                # Apply mesh corrections
                if self.settings.character_rotate_fix and obj.type == 'ARMATURE':
                    rotate_armatures(obj)

                if self.settings.auto_normalize_scale and obj.type == 'MESH':
                    # Check if this is a root object (no parent)
                    if not obj.parent:
                        normalize_object_group_scale(obj)

                # Apply materials to mesh objects
                if obj.type == 'MESH':
                    self._apply_material_to_object(obj, folder_path)

            except Exception as e:
                print(f"[ERROR] Error processing object {obj.name}: {e}")

        # Remove import clutter if requested
        if self.settings.remove_clutter:
            try:
                remove_import_clutter()
            except Exception as e:
                print(f"[WARNING] Failed to remove import clutter: {e}")

    def _apply_material_to_object(self, obj: bpy.types.Object, folder_path: str):
        """Apply material to a mesh object"""
        try:
            original_material = obj.active_material if obj.active_material else None

            # Determine material template
            template_name = self.settings.material_template
            if self.settings.use_emission and template_name == 'standard':
                template_name = 'emissive'

            # Create material settings
            material_settings = {}
            if template_name == 'emissive':
                material_settings['emission_strength'] = 1.0
                material_settings['emission_factor'] = 0.25

            # Create material using factory
            new_material = material_factory.create_material_from_folder(
                obj=obj,
                folder_path=folder_path,
                template_name=template_name,
                force_texture=self.settings.force_texture,
                inherit_from=original_material if self.settings.inherit_material_values else None,
                settings=material_settings
            )

            if new_material:
                # Replace all materials with the new one
                obj.data.materials.clear()
                obj.data.materials.append(new_material)
                print(f"[DEBUG] Applied {template_name} material to {obj.name}")
            else:
                print(f"[WARNING] Failed to create material for {obj.name}")
                if self.settings.use_error_material:
                    error_material = material_factory.create_material('error', obj)
                    if error_material:
                        obj.data.materials.clear()
                        obj.data.materials.append(error_material)

        except Exception as e:
            print(f"[ERROR] Error applying material to {obj.name}: {e}")

    def _process_imported_objects_legacy(self, folder_path: str):
        """Process imported objects using legacy material system"""
        from ..utils.material_operations import assign_new_generated_material
        from ..utils.corrections import rotate_armatures, normalize_object_group_scale
        from ..utils.clean_up import clean_up_clutter

        scene_objects = list(bpy.context.scene.objects)

        for obj in scene_objects:
            try:
                # Apply mesh corrections
                if self.settings.character_rotate_fix and obj.type == 'ARMATURE':
                    rotate_armatures(obj)

                if self.settings.auto_normalize_scale and obj.type == 'MESH':
                    # Check if this is a root object (no parent)
                    if not obj.parent:
                        normalize_object_group_scale(obj)

                # Apply materials to mesh objects using legacy system
                if obj.type == 'MESH':
                    # Find texture files in folder (simple detection)
                    texture_file = ""
                    normal_file = ""

                    try:
                        for filename in os.listdir(folder_path):
                            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                                if 'normal' in filename.lower():
                                    normal_file = os.path.join(folder_path, filename)
                                elif not texture_file:  # Use first non-normal texture found
                                    texture_file = os.path.join(folder_path, filename)
                    except:
                        pass

                    # Apply legacy material
                    assign_new_generated_material(obj, texture_file, normal_file)

            except Exception as e:
                print(f"[ERROR] Legacy processing failed for object {obj.name}: {e}")

        # Remove import clutter if requested
        if self.settings.remove_clutter:
            try:
                for obj in list(bpy.context.scene.objects):
                    clean_up_clutter(obj)
            except Exception as e:
                print(f"[WARNING] Failed to remove import clutter: {e}")

    def _setup_output_folder(self, folder_path: str) -> Optional[str]:
        """Setup output folder for processing"""
        try:
            if self.settings.output_folder:
                # Use specified output folder with relative path structure
                relative_path = os.path.relpath(folder_path, self.settings.input_folder)
                output_folder = os.path.join(self.settings.output_folder, relative_path)
                os.makedirs(output_folder, exist_ok=True)
                return output_folder
            else:
                # Use default output folder creation
                return create_output_folder(folder_path)
        except Exception as e:
            print(f"[ERROR] Failed to setup output folder: {e}")
            return None

    def get_processing_summary(self) -> Dict:
        """Get summary of processing results"""
        summary = self.batch_processor.get_summary()

        # Add cache statistics
        cache_stats = texture_cache.get_cache_stats()
        summary['cache_stats'] = cache_stats

        # Add session duration
        summary['session_duration'] = 0  # Simplified for now

        return summary