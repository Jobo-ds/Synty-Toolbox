import os
import bpy
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from ..utils.logging import logger

# Supported texture formats
TEXTURE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tga', '.exr', '.hdr', '.bmp', '.tiff'}
NORMAL_MAP_KEYWORDS = ['normal', 'nrm', 'norm', 'bump']
DIFFUSE_KEYWORDS = ['diffuse', 'albedo', 'base', 'color', 'diff']

class TextureInfo:
    """Information about a detected texture file"""
    def __init__(self, path: str, texture_type: str, confidence: float = 1.0):
        self.path = path
        self.texture_type = texture_type  # 'diffuse', 'normal', 'roughness', etc.
        self.confidence = confidence
        self.resolution = None
        self.file_size = 0
        self.is_valid = False

        self._validate()

    def _validate(self):
        """Validate the texture file"""
        try:
            if not os.path.exists(self.path):
                logger.warning(f"Texture file not found: {self.path}")
                return

            self.file_size = os.path.getsize(self.path)

            # Try to load image to get resolution
            try:
                # Load without adding to scene
                temp_image = bpy.data.images.load(self.path, check_existing=False)
                self.resolution = (temp_image.size[0], temp_image.size[1])
                # Remove temp image
                bpy.data.images.remove(temp_image)
                self.is_valid = True
                logger.debug(f"Validated texture: {self.path} ({self.resolution[0]}x{self.resolution[1]})")
            except Exception as e:
                logger.warning(f"Could not validate texture {self.path}: {e}")

        except Exception as e:
            logger.error(f"Error validating texture {self.path}: {e}")

class TextureDetector:
    """Advanced texture detection and validation"""

    @staticmethod
    def detect_textures_in_folder(folder_path: str) -> Dict[str, List[TextureInfo]]:
        """Detect all textures in a folder, categorized by type"""
        textures = {
            'diffuse': [],
            'normal': [],
            'roughness': [],
            'metallic': [],
            'emission': [],
            'other': []
        }

        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return textures

        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                if not os.path.isfile(file_path):
                    continue

                ext = Path(filename).suffix.lower()
                if ext not in TEXTURE_EXTENSIONS:
                    continue

                texture_type, confidence = TextureDetector._classify_texture(filename)
                texture_info = TextureInfo(file_path, texture_type, confidence)

                if texture_info.is_valid:
                    textures[texture_type].append(texture_info)
                    logger.debug(f"Detected {texture_type} texture: {filename} (confidence: {confidence:.2f})")

        except Exception as e:
            logger.error(f"Error scanning folder {folder_path}: {e}")

        return textures

    @staticmethod
    def _classify_texture(filename: str) -> Tuple[str, float]:
        """Classify texture type based on filename"""
        name_lower = filename.lower()

        # Check for normal maps first (highest priority)
        for keyword in NORMAL_MAP_KEYWORDS:
            if keyword in name_lower:
                return 'normal', 0.9

        # Check for diffuse/albedo
        for keyword in DIFFUSE_KEYWORDS:
            if keyword in name_lower:
                return 'diffuse', 0.8

        # Check for other common types
        if any(word in name_lower for word in ['rough', 'roughness']):
            return 'roughness', 0.8
        elif any(word in name_lower for word in ['metal', 'metallic', 'metalness']):
            return 'metallic', 0.8
        elif any(word in name_lower for word in ['emit', 'emission', 'emissive']):
            return 'emission', 0.8

        # Default to diffuse if no specific type detected
        return 'diffuse', 0.5

    @staticmethod
    def get_best_texture(textures: List[TextureInfo]) -> Optional[TextureInfo]:
        """Get the best texture from a list based on confidence and resolution"""
        if not textures:
            return None

        # Sort by confidence first, then by resolution
        valid_textures = [t for t in textures if t.is_valid]
        if not valid_textures:
            return None

        return max(valid_textures, key=lambda t: (
            t.confidence,
            t.resolution[0] * t.resolution[1] if t.resolution else 0
        ))

class FileValidator:
    """Validates FBX and other input files"""

    @staticmethod
    def validate_fbx_file(file_path: str) -> Tuple[bool, str]:
        """Validate an FBX file"""
        if not os.path.exists(file_path):
            return False, "File does not exist"

        if not file_path.lower().endswith('.fbx'):
            return False, "Not an FBX file"

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty"

        # Check if it's ASCII FBX (which often causes issues)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(100)
                if b'Kaydara FBX Binary' not in header:
                    logger.warning(f"ASCII FBX detected: {file_path}")
                    return True, "ASCII FBX (may have import issues)"

        except Exception as e:
            logger.warning(f"Could not read FBX header for {file_path}: {e}")

        return True, "Valid binary FBX"

    @staticmethod
    def get_files_with_validation(folder_path: str, extension: str) -> List[Tuple[str, bool, str]]:
        """Get files with validation status"""
        files = []

        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return files

        try:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(f'.{extension.lower()}'):
                    file_path = os.path.join(folder_path, filename)

                    if extension.lower() == 'fbx':
                        is_valid, message = FileValidator.validate_fbx_file(file_path)
                    else:
                        is_valid = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
                        message = "Valid" if is_valid else "Invalid or empty file"

                    files.append((file_path, is_valid, message))

        except Exception as e:
            logger.error(f"Error scanning folder {folder_path}: {e}")

        return files