import bpy
import os
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty  
from .state import flagged_complex_materials, generated_material_counter
import importlib
import sys

# Property Group to store settings
class AssetProcessorSettings(PropertyGroup):
	"""
	Holds all user-configurable options for the asset processor.

	Stored in the Scene to persist between Blender sessions.
	"""

	fbx_folder: StringProperty(
		name="FBX Folder",
		description="Folder containing FBX files to process",
		subtype='DIR_PATH'
	) # type: ignore

	texture_file: StringProperty(
		name="Texture Image",
		description="Base color texture to apply to models",
		subtype='FILE_PATH'
	) # type: ignore

	force_texture: BoolProperty(
		name="Always apply texture",
		description="Apply texture, regardless of original material.",
		default=False
	) # type: ignore

	character_rotate_fix: BoolProperty(
		name="Character Rotate Fix",
		description="Rotate characters upright after import (e.g. if they appear face-down)",
		default=False
	) # type: ignore

	auto_normalize_scale: BoolProperty(
		name="Attempt normalize scale of meshes",
		description="Attempt to rescale meshes by looking for small (x < 1cm) and large (x > 150m) meshes.",
		default=False
	) # type: ignore	


class ASSET_PT_ProcessorPanel(bpy.types.Panel):
	"""
	Sidebar panel to open the Synty Converter popup.

	Appears in the 3D Viewport under the 'Tool' tab.
	Provides a button to launch the interactive processing dialog.
	"""

	bl_label = "Synty Asset Processor"
	bl_idname = "ASSET_PT_ProcessorPanel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tool'  # This will place the panel under the "Tool" tab

	def draw(self, context):
		layout = self.layout
		layout.operator("asset.open_texture_folder_popup", text="Open Synty Converter")
		layout.separator()
		layout.operator("asset.reload_synty_addon", icon='FILE_REFRESH', text="Reload Addon (Dev)")		


# Pop-up Window
class ASSET_OT_OpenTextureFolderPopup(bpy.types.Operator):
	"""
	Popup dialog for selecting input FBX folder and texture file.

	Stores input values into the scene settings and triggers processing.
	Also displays toggle options from the sidebar configuration.
	"""

	bl_idname = "asset.open_texture_folder_popup"
	bl_label = "Texture and Folder Inputs"

	texture_file: StringProperty(name="Texture File", subtype='FILE_PATH')
	input_folder: StringProperty(name="Input Folder", subtype='DIR_PATH')

	def execute(self, context):
		texture_path = self.texture_file
		folder_path = self.input_folder

		# Store popup values into the global scene settings
		settings = context.scene.asset_processor_settings
		settings.texture_file = texture_path
		settings.fbx_folder = folder_path

		# Now invoke the processing operator
		bpy.ops.asset.process_synty_sourcefiles('INVOKE_DEFAULT')

		return {'FINISHED'}

	def invoke(self, context, event):
		"""
		Pre-fills popup fields with values from the scene settings.
		"""

		settings = context.scene.asset_processor_settings
		self.texture_file = settings.texture_file
		self.input_folder = settings.fbx_folder

		return context.window_manager.invoke_props_dialog(self, width=500)

	def draw(self, context):
		"""
		Draws the UI for the popup dialog, including path inputs and scene-linked options.
		"""

		layout = self.layout

		# Section: Header
		layout.label(text="🛠 Synty Sourcefile Converter", icon='FILE_3D')
		layout.separator()

		# Section: Input Paths
		box = layout.box()
		box.label(text="Input Files", icon='FOLDER_REDIRECT')
		box.prop(self, "input_folder", text="FBX Folder")
		box.prop(self, "texture_file", text="Texture Image")

		# Section: Options (from scene settings)
		col = box.column(align=True)
		col.label(text="Options", icon='PREFERENCES')
		col.prop(context.scene.asset_processor_settings, "force_texture", text="Always apply texture")
		col.prop(context.scene.asset_processor_settings, "character_rotate_fix", text="Fix Character Rotation")
		col.prop(context.scene.asset_processor_settings, "auto_normalize_scale", text="Attempt to normalize scale of meshes")

		# Section: Footer
		layout.separator()
		layout.label(text="Click OK to start processing.", icon='INFO')



class ASSET_OT_ReloadAddon(bpy.types.Operator):
	bl_idname = "asset.reload_synty_addon"
	bl_label = "Reload Addon"
	bl_description = "Unregisters and reloads the Synty Sourcefile Converter addon"

	def execute(self, context):
		addon_name = __package__  # dynamically gets your addon folder name

		if addon_name not in sys.modules:
			self.report({'ERROR'}, f"Addon module '{addon_name}' not found in sys.modules")
			return {'CANCELLED'}

		module = sys.modules[addon_name]

		try:
			if hasattr(module, 'unregister'):
				module.unregister()

			importlib.reload(module)

			if hasattr(module, 'register'):
				module.register()

			self.report({'INFO'}, f"Reloaded addon: {addon_name}")
		except Exception as e:
			self.report({'ERROR'}, f"Reload failed: {e}")
			import traceback
			traceback.print_exc()
			return {'CANCELLED'}

		return {'FINISHED'}


# Debug Summary Window
class ASSET_OT_DebugSummary(bpy.types.Operator):
	"""
	Popup summary shown when complex materials are detected during processing.

	Displays a list of flagged materials and gives user the choice to continue or cancel.
	Triggered after batch processing finishes if issues are found.
	"""

	bl_idname = "asset.debug_summary"
	bl_label = "Complex Materials Found"
	bl_options = {'INTERNAL'}

	def execute(self, context):
		"""
		Handles logic when user confirms the debug summary.

		Simply prints confirmation and allows processing to continue.
		"""

		print("[INFO] User chose to continue after debug summary.")
		return {'FINISHED'}

	def invoke(self, context, event):
		"""
		Displays the popup window with a fixed width.

		Invoked automatically when the debug summary operator runs.
		"""

		wm = context.window_manager
		return wm.invoke_popup(self, width=600)

	def draw(self, context):
		"""
		Draws a summary of complex materials and offers Continue/Cancel buttons.

		Iterates through flagged materials and lists node complexity per object.
		"""

		layout = self.layout
		col = layout.column()
		col.label(text="Some materials in the processed files may be complex:")
		col.separator()
		for name, obj, count in flagged_complex_materials:
			col.label(text=f"Material '{name}' on object '{obj}' has {count} nodes.")
		col.separator()
		row = col.row()
		row.operator("asset.debug_summary_continue", text="Continue")
		row.operator("asset.debug_summary_cancel", text="Cancel")


class ASSET_OT_DebugSummaryContinue(bpy.types.Operator):
	"""
	Operator for continuing after viewing the debug summary.

	Used when the user chooses to proceed with GLB exports.
	"""

	bl_idname = "asset.debug_summary_continue"
	bl_label = "Continue Processing"

	def execute(self, context):
		"""
		Completes the operator and resumes processing.

		Returns {'FINISHED'} with no additional actions.
		"""

		return {'FINISHED'}


class ASSET_OT_DebugSummaryCancel(bpy.types.Operator):
	"""
	Operator for halting processing after the debug summary.

	Raises a SystemExit to stop execution immediately.
	"""

	bl_idname = "asset.debug_summary_cancel"
	bl_label = "Cancel Processing"

	def execute(self, context):
		"""
		Logs user cancellation and raises a system exit to halt everything.

		Used to prevent unintended exports when complex materials are found.
		"""
		
		print("[INFO] User canceled processing from debug summary.")
		raise SystemExit("Stopped by user from summary popup.")


# Registration
classes = (
	AssetProcessorSettings,
	ASSET_PT_ProcessorPanel,
	ASSET_OT_OpenTextureFolderPopup,
	ASSET_OT_DebugSummary,
	ASSET_OT_DebugSummaryContinue,
	ASSET_OT_DebugSummaryCancel,
	ASSET_OT_ReloadAddon,
)

def register():
	"""
	Registers all classes and properties for the UI module.

	Called during addon registration to enable panels and popups.
	"""

	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.asset_processor_settings = bpy.props.PointerProperty(type=AssetProcessorSettings)

def unregister():
	"""
	Unregisters all classes and properties defined in the UI module.

	Ensures a clean reload of the addon without leftover classes.
	"""

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.asset_processor_settings
