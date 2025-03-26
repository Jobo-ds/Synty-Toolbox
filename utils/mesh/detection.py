# utils/mesh/detection.py

import bpy

def has_image_texture(material):
	"""
	Checks if a material contains an image texture node.

	Iterates over all nodes in the material's node tree to find a valid image.
	Used to determine whether to reuse texture input or generate a new material.
	"""

	if not material or not material.use_nodes:
		return False

	for node in material.node_tree.nodes:
		if node.type == 'TEX_IMAGE' and node.image is not None:
			return True
	return False