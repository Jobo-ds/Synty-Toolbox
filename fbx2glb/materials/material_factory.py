import bpy
from typing import Dict, Optional, List
from .base_material import StandardPBRMaterial, EmissiveMaterial, ErrorMaterial
# Removed logger import to avoid conflicts
from ...utils.file_detection import TextureDetector

class MaterialTemplate:
    """Template for creating materials with specific settings"""
    def __init__(self, name: str, material_class, default_settings: Dict = None):
        self.name = name
        self.material_class = material_class
        self.default_settings = default_settings or {}

class MaterialFactory:
    """Factory for creating materials with different templates and presets"""

    # Available material templates
    TEMPLATES = {
        'standard': MaterialTemplate('Standard PBR', StandardPBRMaterial),
        'emissive': MaterialTemplate('Emissive (for thumbnails)', EmissiveMaterial, {
            'emission_strength': 1.0,
            'emission_factor': 0.25
        }),
        'stylized': MaterialTemplate('Stylized', StandardPBRMaterial),
        'error': MaterialTemplate('Error Material', ErrorMaterial)
    }

    def __init__(self):
        self.material_counter = 1

    def create_material(self, template_name: str, obj: bpy.types.Object,
                       textures: Dict[str, str] = None,
                       inherit_from: Optional[bpy.types.Material] = None,
                       settings: Dict = None) -> Optional[bpy.types.Material]:
        """Create a material using the specified template"""

        if template_name not in self.TEMPLATES:
            print(f"[ERROR] Unknown material template: {template_name}")
            template_name = 'error'

        template = self.TEMPLATES[template_name]
        material_name = f"{obj.name}_{template.name}_{self.material_counter:03d}"
        self.material_counter += 1

        try:
            # Prepare constructor arguments
            kwargs = {
                'name': material_name,
                'textures': textures or {},
                'inherit_from': inherit_from
            }

            # Add template-specific settings
            if template.default_settings:
                kwargs.update(template.default_settings)

            # Override with user settings
            if settings:
                kwargs.update(settings)

            # Create material using the template
            material_builder = template.material_class(**kwargs)
            material = material_builder.create_material()

            if material:
                print(f"[INFO] Created {template.name} material for {obj.name}")
                return material
            else:
                print(f"[ERROR] Failed to create material for {obj.name}")
                return self._create_fallback_material(obj.name)

        except Exception as e:
            print(f"[ERROR] Error creating material for {obj.name}: {e}")
            return self._create_fallback_material(obj.name)

    def create_material_from_folder(self, obj: bpy.types.Object, folder_path: str,
                                  template_name: str = 'standard',
                                  force_texture: bool = False,
                                  inherit_from: Optional[bpy.types.Material] = None,
                                  settings: Dict = None) -> Optional[bpy.types.Material]:
        """Create material automatically detecting textures from folder"""

        # Detect textures in folder
        detected_textures = TextureDetector.detect_textures_in_folder(folder_path)

        # Build texture map
        texture_map = {}

        # Get best diffuse texture
        best_diffuse = TextureDetector.get_best_texture(detected_textures['diffuse'])
        if best_diffuse:
            texture_map['diffuse'] = best_diffuse.path

        # Get best normal map
        best_normal = TextureDetector.get_best_texture(detected_textures['normal'])
        if best_normal:
            texture_map['normal'] = best_normal.path

        # Get other texture types
        for tex_type in ['roughness', 'metallic', 'emission']:
            best_tex = TextureDetector.get_best_texture(detected_textures[tex_type])
            if best_tex:
                texture_map[tex_type] = best_tex.path

        # Check if we should apply textures
        should_apply_textures = (
            force_texture or
            not inherit_from or
            self._has_image_textures(inherit_from)
        )

        if not should_apply_textures:
            texture_map = {}

        print(f"[DEBUG] Detected textures for {obj.name}: {list(texture_map.keys())}")

        return self.create_material(
            template_name=template_name,
            obj=obj,
            textures=texture_map,
            inherit_from=inherit_from,
            settings=settings
        )

    def _has_image_textures(self, material: bpy.types.Material) -> bool:
        """Check if material has image texture nodes"""
        if not material or not material.use_nodes:
            return False

        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                return True
        return False

    def _create_fallback_material(self, obj_name: str) -> bpy.types.Material:
        """Create a fallback error material"""
        try:
            error_builder = ErrorMaterial(f"ERROR_{obj_name}_{self.material_counter:03d}")
            self.material_counter += 1
            return error_builder.create_material()
        except Exception as e:
            print(f"[ERROR] Failed to create fallback material: {e}")
            return None

    def get_available_templates(self) -> List[str]:
        """Get list of available material templates"""
        return list(self.TEMPLATES.keys())

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """Get information about a template"""
        if template_name in self.TEMPLATES:
            template = self.TEMPLATES[template_name]
            return {
                'name': template.name,
                'class': template.material_class.__name__,
                'default_settings': template.default_settings
            }
        return None

    def reset_counter(self):
        """Reset the material counter"""
        self.material_counter = 1
        print("[DEBUG] Material counter reset")

# Global factory instance
material_factory = MaterialFactory()