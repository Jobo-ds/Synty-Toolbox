import bpy
from ...state import generated_material_counter
from .detection import has_image_texture
# Removed logger import to avoid conflicts
from ..materials.material_factory import material_factory

def create_new_generated_material():
	"""
	Creates a new empty Blender material with a unique name.

	Initializes a node-based material and clears any default nodes.
	Used to assign a fresh material to imported objects.
	"""

	global generated_material_counter
	name = f"Generated_Material_{generated_material_counter:03d}"
	generated_material_counter += 1

	mat = bpy.data.materials.new(name)
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	nodes.clear()  # Clean slate
	return mat

def add_bsdf_node(material, original_material, inherit_values=True):
	"""
	Adds a Principled BSDF node to the material, optionally attempting to inherit values from the original.

	"""

	nodes = material.node_tree.nodes
	bsdf = nodes.new("ShaderNodeBsdfPrincipled")
	bsdf.location = (0, 0)

	base_color = (0.8, 0.8, 0.8, 1.0)
	roughness = 0.5
	metallic = 0.0
	alpha = 1.0

	if inherit_values and original_material and original_material.use_nodes:
		for node in original_material.node_tree.nodes:
			if node.type == "BSDF_PRINCIPLED":
				base_color = node.inputs["Base Color"].default_value[:]
				roughness = node.inputs["Roughness"].default_value
				metallic = node.inputs["Metallic"].default_value
				alpha = node.inputs["Alpha"].default_value
				break

	bsdf.inputs["Base Color"].default_value = base_color
	bsdf.inputs["Roughness"].default_value = roughness
	bsdf.inputs["Metallic"].default_value = metallic
	bsdf.inputs["Alpha"].default_value = alpha

	# Optional: ensure material is set up for transparency
	material.blend_method = 'BLEND'
	if hasattr(material, 'shadow_method'):
		material.shadow_method = 'HASHED'
	material.use_backface_culling = False 

	return bsdf

def add_texture_node(material, bsdf_node, texture_path):
	"""
	Adds an image texture node and connects it to the BSDF base color input.

	Loads the given texture file and links it into the material.
	Returns the created texture node for optional reuse.
	"""

	nodes = material.node_tree.nodes
	links = material.node_tree.links

	tex_image = nodes.new("ShaderNodeTexImage")
	tex_image.image = bpy.data.images.load(texture_path, check_existing=True)
	tex_image.location = (-300, 0)

	links.new(tex_image.outputs["Color"], bsdf_node.inputs["Base Color"])

	return tex_image  # <-- RETURN IT!

def add_emission_layer(material, bsdf_node, texture_node=None, strength=1.0, factor=0.25):
	nodes = material.node_tree.nodes
	links = material.node_tree.links

	emission = nodes.new("ShaderNodeEmission")
	emission.inputs["Strength"].default_value = strength
	emission.location = (200, -200)

	mix = nodes.new("ShaderNodeMixShader")
	mix.inputs["Fac"].default_value = factor
	mix.location = (400, 0)

	# If we have a texture, connect it to Emission color too
	if texture_node:
		links.new(texture_node.outputs["Color"], emission.inputs["Color"])
	else:
		# Use BSDF base color input as fallback
		emission.inputs["Color"].default_value = bsdf_node.inputs["Base Color"].default_value

	links.new(bsdf_node.outputs["BSDF"], mix.inputs[1])
	links.new(emission.outputs["Emission"], mix.inputs[2])
	return mix

def add_output_node(material, shader_output):
	"""
	Adds a Material Output node and connects it to the given shader output.

	Finalizes the material's node tree by linking the shader to the surface output.
	Should be called last when constructing the shader graph.
	"""

	nodes = material.node_tree.nodes
	links = material.node_tree.links

	output = nodes.new("ShaderNodeOutputMaterial")
	output.location = (600, 0)

	links.new(shader_output.outputs[0], output.inputs["Surface"])

def create_error_material(name="ERROR_MATERIAL"):
	"""
	Creates a fallback error material with a checker and emission shader.

	Used to visually indicate missing or invalid materials.
	Returns the created error material.
	"""

	mat = bpy.data.materials.new(name=name)
	mat.use_nodes = True
	mat.blend_method = 'OPAQUE'
	if hasattr(mat, 'shadow_method'):
		mat.shadow_method = 'NONE'

	nodes = mat.node_tree.nodes
	links = mat.node_tree.links
	nodes.clear()

	checker = nodes.new("ShaderNodeTexChecker")
	checker.inputs['Scale'].default_value = 15.0

	emission = nodes.new("ShaderNodeEmission")
	emission.inputs["Strength"].default_value = 5.0  # Brighter

	output = nodes.new("ShaderNodeOutputMaterial")

	links.new(checker.outputs["Color"], emission.inputs["Color"])
	links.new(emission.outputs["Emission"], output.inputs["Surface"])

	return mat


def assign_new_generated_material(obj, texture_path=None, normal_map_path=None):
	"""
	Legacy function for backward compatibility.
	Uses the new material factory system internally.
	"""
	try:
		scene = bpy.context.scene
		settings = scene.fbx2glb_props

		# Build texture map for new system
		textures = {}
		if texture_path:
			textures['diffuse'] = texture_path
		if normal_map_path:
			textures['normal'] = normal_map_path

		# Determine template based on settings
		template_name = getattr(settings, 'material_template', 'standard')
		if settings.use_emission and template_name == 'standard':
			template_name = 'emissive'

		# Get original material
		original_material = obj.active_material if obj.active_material else None

		# Use new material factory
		material = material_factory.create_material(
			template_name=template_name,
			obj=obj,
			textures=textures,
			inherit_from=original_material if settings.inherit_material_values else None,
			settings={
				'emission_strength': getattr(settings, 'emission_strength', 1.0),
				'emission_factor': getattr(settings, 'emission_factor', 0.25)
			}
		)

		if material:
			obj.data.materials.clear()
			obj.data.materials.append(material)
			print(f"[DEBUG] Applied material to {obj.name} using legacy interface")
		else:
			print(f"[ERROR] Failed to create material for {obj.name}")
			if settings.use_error_material:
				error_material = material_factory.create_material('error', obj)
				if error_material:
					obj.data.materials.clear()
					obj.data.materials.append(error_material)

	except Exception as e:
		print(f"[ERROR] Material assignment failed on {obj.name}: {e}")
		scene = bpy.context.scene
		settings = scene.fbx2glb_props
		if settings.use_error_material:
			try:
				error_material = material_factory.create_material('error', obj)
				if error_material:
					obj.data.materials.clear()
					obj.data.materials.append(error_material)
			except Exception as e2:
				print(f"[ERROR] Failed to create error material: {e2}")


