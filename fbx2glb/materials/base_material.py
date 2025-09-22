import bpy
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
# Removed logger import to avoid conflicts
from ...utils.texture_cache import texture_cache

class MaterialNode:
    """Represents a shader node with its properties and connections"""
    def __init__(self, node_type: str, location: tuple = (0, 0), properties: Dict[str, Any] = None):
        self.node_type = node_type
        self.location = location
        self.properties = properties or {}
        self.connections = []  # List of (output_socket, input_socket) tuples

class BaseMaterial(ABC):
    """Base class for all material builders"""

    def __init__(self, name: str):
        self.name = name
        self.material = None
        self.nodes = {}
        self.node_tree = None

    def create_material(self) -> Optional[bpy.types.Material]:
        """Create and return the complete material"""
        try:
            self.material = bpy.data.materials.new(name=self.name)
            self.material.use_nodes = True
            self.node_tree = self.material.node_tree
            self.node_tree.nodes.clear()

            # Build the material
            self._build_nodes()
            self._setup_connections()
            self._configure_material_properties()

            print(f"[DEBUG] Created material: {self.name}")
            return self.material

        except Exception as e:
            print(f"[ERROR] Failed to create material {self.name}: {e}")
            return None

    @abstractmethod
    def _build_nodes(self):
        """Build all required nodes for this material type"""
        pass

    @abstractmethod
    def _setup_connections(self):
        """Setup connections between nodes"""
        pass

    def _configure_material_properties(self):
        """Configure material-level properties (blend mode, etc.)"""
        if self.material:
            self.material.blend_method = 'BLEND'
            # shadow_method was removed in Blender 4.0+
            if hasattr(self.material, 'shadow_method'):
                self.material.shadow_method = 'HASHED'
            self.material.use_backface_culling = False

    def add_node(self, key: str, node_type: str, location: tuple = (0, 0)) -> Optional[bpy.types.Node]:
        """Add a node to the material"""
        try:
            node = self.node_tree.nodes.new(node_type)
            node.location = location
            self.nodes[key] = node
            return node
        except Exception as e:
            print(f"[ERROR] Failed to add node {node_type}: {e}")
            return None

    def connect_nodes(self, output_node_key: str, output_socket: str,
                     input_node_key: str, input_socket: str):
        """Connect two nodes"""
        try:
            output_node = self.nodes[output_node_key]
            input_node = self.nodes[input_node_key]
            self.node_tree.links.new(
                output_node.outputs[output_socket],
                input_node.inputs[input_socket]
            )
            print(f"[DEBUG] Connected {output_node_key}.{output_socket} -> {input_node_key}.{input_socket}")
        except Exception as e:
            print(f"[ERROR] Failed to connect nodes: {e}")

    def add_texture_node(self, key: str, texture_path: str, location: tuple = (0, 0),
                        colorspace: str = 'sRGB') -> Optional[bpy.types.Node]:
        """Add a texture node with cached image loading"""
        if not texture_path:
            return None

        try:
            texture_node = self.add_node(key, "ShaderNodeTexImage", location)
            if texture_node:
                image = texture_cache.get_texture(texture_path)
                if image:
                    texture_node.image = image
                    if colorspace != 'sRGB':
                        image.colorspace_settings.name = colorspace
                    print(f"[DEBUG] Added texture node {key} with image: {texture_path}")
                    return texture_node
                else:
                    print(f"[WARNING] Failed to load texture for {key}: {texture_path}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to add texture node {key}: {e}")
            return None

class StandardPBRMaterial(BaseMaterial):
    """Standard PBR material with support for common texture maps"""

    def __init__(self, name: str, textures: Dict[str, str] = None,
                 inherit_from: Optional[bpy.types.Material] = None):
        super().__init__(name)
        self.textures = textures or {}
        self.inherit_from = inherit_from

    def _build_nodes(self):
        """Build PBR material nodes"""
        # Main BSDF shader
        bsdf = self.add_node('bsdf', "ShaderNodeBsdfPrincipled", (0, 0))

        # Set default values or inherit from original material
        if self.inherit_from and self.inherit_from.use_nodes:
            self._inherit_bsdf_values(bsdf)
        else:
            self._set_default_bsdf_values(bsdf)

        # Add texture nodes
        y_offset = 0
        if 'diffuse' in self.textures:
            self.add_texture_node('diffuse', self.textures['diffuse'], (-300, y_offset))
            y_offset -= 300

        if 'normal' in self.textures:
            self.add_texture_node('normal', self.textures['normal'], (-300, y_offset), 'Non-Color')
            normal_map = self.add_node('normal_map', "ShaderNodeNormalMap", (-100, y_offset))
            y_offset -= 300

        if 'roughness' in self.textures:
            self.add_texture_node('roughness', self.textures['roughness'], (-300, y_offset), 'Non-Color')
            y_offset -= 300

        if 'metallic' in self.textures:
            self.add_texture_node('metallic', self.textures['metallic'], (-300, y_offset), 'Non-Color')
            y_offset -= 300

        # Output node
        self.add_node('output', "ShaderNodeOutputMaterial", (600, 0))

    def _setup_connections(self):
        """Setup node connections"""
        # Connect diffuse texture if available
        if 'diffuse' in self.nodes:
            self.connect_nodes('diffuse', 'Color', 'bsdf', 'Base Color')

        # Connect normal map if available
        if 'normal' in self.nodes and 'normal_map' in self.nodes:
            self.connect_nodes('normal', 'Color', 'normal_map', 'Color')
            self.connect_nodes('normal_map', 'Normal', 'bsdf', 'Normal')

        # Connect roughness if available
        if 'roughness' in self.nodes:
            self.connect_nodes('roughness', 'Color', 'bsdf', 'Roughness')

        # Connect metallic if available
        if 'metallic' in self.nodes:
            self.connect_nodes('metallic', 'Color', 'bsdf', 'Metallic')

        # Connect to output
        self.connect_nodes('bsdf', 'BSDF', 'output', 'Surface')

    def _inherit_bsdf_values(self, bsdf_node):
        """Inherit values from original material"""
        for node in self.inherit_from.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                try:
                    bsdf_node.inputs["Base Color"].default_value = node.inputs["Base Color"].default_value[:]
                    bsdf_node.inputs["Roughness"].default_value = node.inputs["Roughness"].default_value
                    bsdf_node.inputs["Metallic"].default_value = node.inputs["Metallic"].default_value
                    bsdf_node.inputs["Alpha"].default_value = node.inputs["Alpha"].default_value
                    print("[DEBUG] Inherited BSDF values from original material")
                except Exception as e:
                    print(f"[WARNING] Failed to inherit some BSDF values: {e}")
                break

    def _set_default_bsdf_values(self, bsdf_node):
        """Set default PBR values"""
        bsdf_node.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1.0)
        bsdf_node.inputs["Roughness"].default_value = 0.5
        bsdf_node.inputs["Metallic"].default_value = 0.0
        bsdf_node.inputs["Alpha"].default_value = 1.0

class EmissiveMaterial(StandardPBRMaterial):
    """PBR material with emission for thumbnails"""

    def __init__(self, name: str, textures: Dict[str, str] = None,
                 inherit_from: Optional[bpy.types.Material] = None,
                 emission_strength: float = 1.0, emission_factor: float = 0.25):
        super().__init__(name, textures, inherit_from)
        self.emission_strength = emission_strength
        self.emission_factor = emission_factor

    def _build_nodes(self):
        """Build nodes with emission layer"""
        super()._build_nodes()

        # Add emission nodes
        emission = self.add_node('emission', "ShaderNodeEmission", (200, -200))
        emission.inputs["Strength"].default_value = self.emission_strength

        mix_shader = self.add_node('mix_shader', "ShaderNodeMixShader", (400, 0))
        mix_shader.inputs["Fac"].default_value = self.emission_factor

    def _setup_connections(self):
        """Setup connections including emission"""
        # Setup base PBR connections first
        super()._setup_connections()

        # Disconnect BSDF from output and route through mix shader
        # Remove existing connection
        for link in self.node_tree.links:
            if (link.from_node == self.nodes['bsdf'] and
                link.to_node == self.nodes['output']):
                self.node_tree.links.remove(link)
                break

        # Connect emission
        if 'diffuse' in self.nodes:
            self.connect_nodes('diffuse', 'Color', 'emission', 'Color')
        else:
            # Use BSDF base color as fallback
            emission_node = self.nodes['emission']
            emission_node.inputs["Color"].default_value = self.nodes['bsdf'].inputs["Base Color"].default_value

        # Connect through mix shader
        self.connect_nodes('bsdf', 'BSDF', 'mix_shader', 'Shader')
        self.connect_nodes('emission', 'Emission', 'mix_shader', 'Shader_001')
        self.connect_nodes('mix_shader', 'Shader', 'output', 'Surface')

class ErrorMaterial(BaseMaterial):
    """Bright error material for debugging"""

    def __init__(self, name: str = "ERROR_MATERIAL"):
        super().__init__(name)

    def _build_nodes(self):
        """Build error material nodes"""
        checker = self.add_node('checker', "ShaderNodeTexChecker", (-200, 0))
        checker.inputs['Scale'].default_value = 15.0

        emission = self.add_node('emission', "ShaderNodeEmission", (0, 0))
        emission.inputs["Strength"].default_value = 5.0

        self.add_node('output', "ShaderNodeOutputMaterial", (200, 0))

    def _setup_connections(self):
        """Setup error material connections"""
        self.connect_nodes('checker', 'Color', 'emission', 'Color')
        self.connect_nodes('emission', 'Emission', 'output', 'Surface')

    def _configure_material_properties(self):
        """Configure error material properties"""
        if self.material:
            self.material.blend_method = 'OPAQUE'
            # shadow_method was removed in Blender 4.0+
            if hasattr(self.material, 'shadow_method'):
                self.material.shadow_method = 'NONE'