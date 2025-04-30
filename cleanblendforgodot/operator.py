import bpy
import os
from bpy.types import Operator

class SSTOOL_OT_CleanBlendOperator(Operator):
	bl_idname = "sstool.clean_blend_execute"
	bl_label = "Execute Clean Blend"

	def execute(self, context):
		props = context.scene.sstool_clean_blend_props

		folder = props.blend_folder
		image_path = props.image_path
		base_name = props.material_name

		if not os.path.isdir(folder) or not os.path.isfile(image_path):
			self.report({'ERROR'}, "Invalid path.")
			return {'CANCELLED'}

		for file in os.listdir(folder):
			if file.lower().endswith(".blend"):
				bpy.ops.wm.open_mainfile(filepath=os.path.join(folder, file))

				image_name = os.path.basename(image_path)
				image = bpy.data.images.get(image_name)
				if not image:
					image = bpy.data.images.load(image_path)

				for img in bpy.data.images:
					if img.packed_file:
						try:
							img.unpack(method='USE_ORIGINAL')
						except:
							pass

				for i, mat in enumerate(bpy.data.materials):
					if mat.use_nodes:
						mat.name = base_name if i == 0 else f"{base_name}.{i:03d}"
						for node in mat.node_tree.nodes:
							if node.type == 'TEX_IMAGE':
								node.image = image

				bpy.ops.wm.save_mainfile(filepath=os.path.join(folder, file))

		self.report({'INFO'}, "Blend files processed.")
		return {'FINISHED'}
