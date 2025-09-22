import bpy
import os
from typing import Dict, Optional
from ..utils.logging import logger

class TextureCache:
    """Cache system for loaded textures to improve performance"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache = {}
            cls._instance.usage_count = {}
        return cls._instance

    def get_texture(self, texture_path: str) -> Optional[bpy.types.Image]:
        """Get texture from cache or load if not cached"""
        if not os.path.exists(texture_path):
            logger.error(f"Texture file not found: {texture_path}")
            return None

        # Normalize path for consistent caching
        normalized_path = os.path.normpath(texture_path)

        if normalized_path in self.cache:
            # Check if the cached image is still valid
            cached_image = self.cache[normalized_path]
            if cached_image and cached_image.name in bpy.data.images:
                self.usage_count[normalized_path] = self.usage_count.get(normalized_path, 0) + 1
                logger.debug(f"Using cached texture: {texture_path}")
                return cached_image
            else:
                # Remove invalid cache entry
                del self.cache[normalized_path]
                if normalized_path in self.usage_count:
                    del self.usage_count[normalized_path]

        # Load new texture
        try:
            image = bpy.data.images.load(texture_path, check_existing=True)
            self.cache[normalized_path] = image
            self.usage_count[normalized_path] = 1
            logger.debug(f"Loaded and cached texture: {texture_path}")
            return image
        except Exception as e:
            logger.error(f"Failed to load texture {texture_path}: {e}")
            return None

    def clear_cache(self):
        """Clear the texture cache"""
        logger.info(f"Clearing texture cache ({len(self.cache)} items)")
        self.cache.clear()
        self.usage_count.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cached_textures': len(self.cache),
            'total_usage': sum(self.usage_count.values()),
            'cache_hits': sum(count - 1 for count in self.usage_count.values() if count > 1)
        }

    def cleanup_unused(self):
        """Remove unused textures from cache"""
        to_remove = []
        for path, image in self.cache.items():
            if not image or image.name not in bpy.data.images:
                to_remove.append(path)

        for path in to_remove:
            del self.cache[path]
            if path in self.usage_count:
                del self.usage_count[path]

        if to_remove:
            print(f"[INFO] Cleaned up {len(to_remove)} unused textures from cache")

    def is_image_cached(self, image_name: str) -> bool:
        """Check if an image is in the cache by name"""
        for cached_image in self.cache.values():
            if cached_image and cached_image.name == image_name:
                return True
        return False

    def protect_cached_images(self):
        """Mark cached images to prevent them from being cleared"""
        protected_images = []
        for path, image in self.cache.items():
            if image and image.name in bpy.data.images:
                # Add a custom property to mark as cached
                image['_synty_cached'] = True
                protected_images.append(image.name)

        if protected_images:
            print(f"[DEBUG] Protected {len(protected_images)} cached images from clearing")

# Singleton instance
texture_cache = TextureCache()