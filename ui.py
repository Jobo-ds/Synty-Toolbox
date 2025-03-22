import bpy
import os
from bpy.types import Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty  
from .state import flagged_complex_materials, generated_material_counter

# Property Group to store settings
class AssetProcessorSettings(PropertyGroup):
	"""
	Holds all user-configurable options for the asset processor.

	Includes folder paths and toggle options like 'use_emission' and 'dry_run'.
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

	dry_run: BoolProperty(
		name="Dry Run",
		description="Simulate the process without exporting GLB files",
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


# Pop-up Window
class ASSET_OT_OpenTextureFolderPopup(bpy.types.Operator):
	"""
	Popup dialog for selecting input FBX folder and texture file.

	Stores input values into the scene settings and triggers processing.
	Also displays mock toggle options and a basic UI layout.
	"""

	bl_idname = "asset.open_texture_folder_popup"
	bl_label = "Texture and Folder Inputs"

	texture_file: StringProperty(name="Texture File", subtype='FILE_PATH')
	input_folder: StringProperty(name="Input Folder", subtype='DIR_PATH')

	def execute(self, context):
		"""
		Validates user input and starts the FBX processing operation.

		Stores folder and texture path into scene settings and invokes processing.
		Returns {'FINISHED'} on success, otherwise {'CANCELLED'} on invalid input.
		"""

		if not os.path.isfile(self.texture_file):
			self.report({'ERROR'}, "Please select a valid texture file.")
			return {'CANCELLED'}

		if not os.path.isdir(self.input_folder):
			self.report({'ERROR'}, "Please select a valid FBX folder.")
			return {'CANCELLED'}

		# Store values in the Scene's settings for the actual processor to use
		settings = context.scene.asset_processor_settings
		settings.texture_file = self.texture_file
		settings.fbx_folder = self.input_folder

		bpy.ops.asset.process_synty_sourcefiles('INVOKE_DEFAULT')
		return {'FINISHED'}


	def invoke(self, context, event):
		"""
		Opens the popup dialog with defined layout and width.

		Called automatically when operator is invoked.
		"""
		
		wm = context.window_manager
		return wm.invoke_props_dialog(self, width=500)

	def draw(self, context):
		"""
		Draws the UI for the popup dialog, including path inputs and options.

		Organized into sections for input files, mock options, and footer message.
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

		# Section: Options (Mockups for now)
		box = layout.box()
		box.label(text="Options", icon='PREFERENCES')
		box.prop(context.scene.asset_processor_settings, "force_texture", text="Always apply texture")

		# Section: Footer
		layout.separator()
		layout.label(text="Click OK to start processing.", icon='INFO')



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
