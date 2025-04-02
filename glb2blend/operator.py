import bpy
from bpy.types import Operator
import pathlib
from ..utils.blender import clear_scene

def add_suffix_to_all_objects(suffix="-col"):
	for obj in bpy.data.objects:
		if not obj.name.endswith(suffix):
			obj.name = f"{obj.name}{suffix}"
		if hasattr(obj.data, "name") and not obj.data.name.endswith(suffix):
			obj.data.name = f"{obj.data.name}{suffix}"

class SSTOOL_OT_GLB2BlendOperator(Operator):
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
			clear_scene()  # ✅ SAFE scene reset

			rel_path = glb_path.relative_to(input_dir).with_suffix("")
			output_blend_path = output_dir / rel_path
			output_blend_path.parent.mkdir(parents=True, exist_ok=True)

			bpy.ops.import_scene.gltf(filepath=str(glb_path))

			if props.use_col_suffix:
				add_suffix_to_all_objects()

			bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path.with_suffix(".blend")))

		clear_scene()  # ✅ Final cleanup

		self.report({'INFO'}, f"Converted {len(glb_files)} files")
		return {'FINISHED'}
