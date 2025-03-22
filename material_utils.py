import bpy
from .state import flagged_complex_materials, generated_material_counter
from .fbx_handler import has_image_texture

def create_new_generated_material():
	global generated_material_counter
	name = f"Generated_Material_{generated_material_counter:03d}"
	generated_material_counter += 1

	mat = bpy.data.materials.new(name)
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	nodes.clear()  # Clean slate
	return mat

def add_bsdf_node_with_inheritance(material, original_material):
	nodes = material.node_tree.nodes
	bsdf = nodes.new("ShaderNodeBsdfPrincipled")
	bsdf.location = (0, 0)

	# Set default values
	base_color = (0.8, 0.8, 0.8, 1.0)
	roughness = 0.5
	metallic = 0.0
	alpha = 1.0

	if original_material and original_material.use_nodes:
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
	material.shadow_method = 'HASHED'
	material.use_backface_culling = False 

	return bsdf

def add_texture_node(material, bsdf_node, texture_path):
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
	nodes = material.node_tree.nodes
	links = material.node_tree.links

	output = nodes.new("ShaderNodeOutputMaterial")
	output.location = (600, 0)

	links.new(shader_output.outputs[0], output.inputs["Surface"])

def create_error_material(name="ERROR_MATERIAL"):
	mat = bpy.data.materials.new(name=name)
	mat.use_nodes = True
	mat.blend_method = 'OPAQUE'
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


def assign_new_generated_material(obj, texture_path, use_emission=True):
    original_material = obj.active_material if obj.active_material else None

    new_mat = create_new_generated_material()
    bsdf = add_bsdf_node_with_inheritance(new_mat, original_material)

    texture_node = None
    if original_material and has_image_texture(original_material):
        texture_node = add_texture_node(new_mat, bsdf, texture_path)

    shader_output = (
        add_emission_layer(new_mat, bsdf, texture_node)
        if use_emission else bsdf
    )

    add_output_node(new_mat, shader_output)

    obj.data.materials.clear()
    obj.data.materials.append(new_mat)
