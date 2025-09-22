import bpy
import os
from bpy.types import Operator
from ..utils.file_detection import FileValidator, TextureDetector
from ..utils.logging import logger

class SSTOOL_OT_PreviewBatchOperator(Operator):
    bl_idname = "sstool.preview_batch"
    bl_label = "Preview Batch"
    bl_description = "Preview what files will be processed before starting"
    bl_options = {'REGISTER'}

    def execute(self, context):
        """Preview the batch processing operation"""
        try:
            props = context.scene.fbx2glb_props

            if not props.fbx_folder:
                self.report({'ERROR'}, "No input folder specified")
                return {'CANCELLED'}

            # Get folders to analyze
            folders = [props.fbx_folder]
            if props.search_subfolders:
                from ..utils.folder_operations import get_subfolders
                folders = get_subfolders(props.fbx_folder, "fbx")

            total_files = 0
            valid_files = 0
            invalid_files = 0
            folders_with_textures = 0

            preview_info = []

            for folder in folders:
                if not os.path.exists(folder):
                    continue

                # Analyze FBX files
                files_with_validation = FileValidator.get_files_with_validation(folder, "fbx")
                folder_files = len(files_with_validation)
                folder_valid = sum(1 for _, is_valid, _ in files_with_validation if is_valid)
                folder_invalid = folder_files - folder_valid

                # Analyze textures
                textures = TextureDetector.detect_textures_in_folder(folder)
                has_diffuse = len(textures['diffuse']) > 0
                has_normal = len(textures['normal']) > 0

                if has_diffuse or has_normal:
                    folders_with_textures += 1

                preview_info.append({
                    'folder': folder,
                    'total_files': folder_files,
                    'valid_files': folder_valid,
                    'invalid_files': folder_invalid,
                    'has_diffuse': has_diffuse,
                    'has_normal': has_normal,
                    'diffuse_count': len(textures['diffuse']),
                    'normal_count': len(textures['normal'])
                })

                total_files += folder_files
                valid_files += folder_valid
                invalid_files += folder_invalid

            # Generate preview report
            if total_files == 0:
                self.report({'WARNING'}, "No FBX files found to process")
                return {'CANCELLED'}

            # Show preview in console
            logger.info("=== BATCH PROCESSING PREVIEW ===")
            logger.info(f"Total folders: {len(folders)}")
            logger.info(f"Total FBX files: {total_files}")
            logger.info(f"Valid files: {valid_files}")
            logger.info(f"Invalid files: {invalid_files}")
            logger.info(f"Folders with textures: {folders_with_textures}")

            for info in preview_info:
                folder_name = os.path.basename(info['folder'])
                texture_info = ""
                if info['has_diffuse']:
                    texture_info += f"{info['diffuse_count']} diffuse"
                if info['has_normal']:
                    if texture_info:
                        texture_info += f", {info['normal_count']} normal"
                    else:
                        texture_info += f"{info['normal_count']} normal"

                logger.info(f"  {folder_name}: {info['valid_files']}/{info['total_files']} files" +
                           (f", textures: {texture_info}" if texture_info else ", no textures"))

            logger.info("=== END PREVIEW ===")

            # Report summary to user
            if invalid_files > 0:
                self.report({'WARNING'},
                           f"Preview: {valid_files} valid files, {invalid_files} invalid files. Check console for details.")
            else:
                self.report({'INFO'},
                           f"Preview: {valid_files} files ready to process in {len(folders)} folders")

            return {'FINISHED'}

        except Exception as e:
            logger.error(f"Preview failed: {e}")
            self.report({'ERROR'}, f"Preview failed: {e}")
            return {'CANCELLED'}