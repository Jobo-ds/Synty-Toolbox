import bpy

class SSTOOL_OT_GLB2BlendPopup(bpy.types.Operator):
	bl_idname = "sstool.glb2blend_popup"
	bl_label = "GLB to Blend Converter"

	def execute(self, context):
		# Launch the actual conversion operator
		bpy.ops.object.convert_glb_to_blend('INVOKE_DEFAULT')
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width=800)

	def draw(self, context):
		layout = self.layout

		# Check if properties exist
		if not hasattr(context.scene, 'glb2blend_props'):
			layout.label(text="ERROR: Properties not found. Please restart Blender or reinstall the addon.", icon='ERROR')
			return

		props = context.scene.glb2blend_props

		layout.label(text="GLB to Blend Converter Settings")

		# Main two-column layout
		split = layout.split(factor=0.5, align=True)
		left_col = split.column(align=True)
		right_col = split.column(align=True)

		# LEFT COLUMN
		# --- Input/Output Section ---
		left_col.label(text="📂 Input/Output", icon='NONE')
		box = left_col.box()
		box.prop(props, "input_dir", text="GLB Folder")
		box.prop(props, "output_dir", text="Output Folder")

		# --- Output Options ---
		left_col.separator()
		left_col.label(text="📦 Output Mode", icon='NONE')
		box = left_col.box()
		box.prop(props, "output_mode", text="Mode")
		if props.output_mode == 'MERGE_ALL':
			box.label(text="All GLBs → single .blend", icon='INFO')
		elif props.output_mode == 'MERGE_FOLDER':
			box.label(text="Folder GLBs → merged .blend", icon='INFO')
		else:
			box.label(text="Each GLB → individual .blend", icon='INFO')

		box.prop(props, "backup_existing", text="Backup Existing")

		# --- Import Options ---
		left_col.separator()
		left_col.label(text="📥 Import", icon='NONE')
		box = left_col.box()
		box.prop(props, "import_materials", text="Materials")
		box.prop(props, "import_animations", text="Animations")
		row = box.row()
		row.prop(props, "import_cameras", text="Cameras")
		row.prop(props, "import_lights", text="Lights")

		# --- Scale Options ---
		left_col.separator()
		left_col.label(text="📏 Scale", icon='NONE')
		box = left_col.box()
		box.prop(props, "uniform_scale", text="Scale Factor")
		box.prop(props, "apply_scale", text="Apply to Mesh")

		# RIGHT COLUMN
		# --- Organization ---
		right_col.label(text="🗂️ Organization", icon='NONE')
		box = right_col.box()
		box.prop(props, "organize_collections", text="Use Collections")
		if props.organize_collections:
			box.prop(props, "collection_naming", text="Naming")
			if props.collection_naming == 'CUSTOM':
				box.prop(props, "custom_collection_pattern", text="Pattern")

		box.prop(props, "preserve_hierarchy", text="Preserve Hierarchy")

		# --- Naming Options ---
		right_col.separator()
		right_col.label(text="🏷️ Naming", icon='NONE')
		box = right_col.box()
		box.prop(props, "use_col_suffix", text="Add '-col' suffix")
		box.prop(props, "custom_object_suffix", text="Custom Suffix")

		# --- Processing Options ---
		right_col.separator()
		right_col.label(text="⚙️ Processing", icon='NONE')
		box = right_col.box()
		box.prop(props, "continue_on_error", text="Continue on Error")
		box.prop(props, "validate_glb_files", text="Validate Files")
		box.prop(props, "clear_scene_between", text="Clear Scene")
		box.prop(props, "show_processing_log", text="Detailed Log")

		# --- Performance ---
		right_col.separator()
		right_col.label(text="🚀 Performance", icon='NONE')
		box = right_col.box()
		row = box.row()
		row.prop(props, "batch_size", text="Batch Size")
		row.prop(props, "memory_limit_mb", text="Memory Limit")

		# Bottom buttons (full width)
		layout.separator()
		row = layout.row()
		row.scale_y = 1.2
		row.operator("object.convert_glb_to_blend", text="Convert GLB to Blend", icon='EXPORT')
		row.operator("object.test_glb2blend_converter", text="Test Single File", icon='PLAY')

		# Preview info
		layout.separator()
		box = layout.box()
		box.label(text="Preview Settings:", icon='INFO')

		# Show current settings summary
		col = box.column(align=True)
		col.label(text=f"Output: {props.output_mode.replace('_', ' ').title()}")
		col.label(text=f"Materials: {props.import_materials.replace('_', ' ').title()}")
		if props.organize_collections:
			col.label(text=f"Collections: {props.collection_naming.replace('_', ' ').title()}")
		if props.uniform_scale != 1.0:
			col.label(text=f"Scale: {props.uniform_scale}x")
		