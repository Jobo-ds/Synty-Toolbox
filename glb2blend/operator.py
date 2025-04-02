import bpy
from bpy.types import Operator
import pathlib

class ConvertGLBToBlendOperator(Operator):
	bl_idname = "object.convert_glb_to_blend"
	bl_label = "Convert GLB to Blend (Recursive)"

	def execute(self, context):
		props = context.scene.glb2blend_props
		input_dir = pathlib.Path(bpy.path.abspath(props.input_dir))
		output_dir = pathlib.Path(bpy.path.abspath(props.output_dir))

		if not input_dir.exists() or not output_dir.exists():
			self.report({'ERROR'}, "Invalid input or output directory")
			return {'CANCELLED'}

		glb_files = list(input_dir.rglob("*.glb"))

		for glb_path in glb_files:
			rel_path = glb_path.relative_to(input_dir).with_suffix("")
			output_blend_path = output_dir / rel_path
			output_blend_path.parent.mkdir(parents=True, exist_ok=True)

			bpy.ops.wm.read_factory_settings(use_empty=True)
			bpy.ops.import_scene.gltf(filepath=str(glb_path))

			bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path.with_suffix(".blend")))

		self.report({'INFO'}, f"Converted {len(glb_files)} files")
		return {'FINISHED'}