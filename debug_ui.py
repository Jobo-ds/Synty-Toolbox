import bpy
from .state import flagged_complex_materials, generated_material_counter

class ASSET_OT_DebugPrompt(bpy.types.Operator):
	"""
	Popup operator that shows a warning about complex materials.

	Displays a message split into lines and offers Continue or Cancel actions.
	Used to inform users before processing continues with potentially problematic materials.
	"""

	bl_idname = "asset.debug_prompt"
	bl_label = "Complex Material Detected"
	bl_options = {'INTERNAL'}

	message: bpy.props.StringProperty()

	def execute(self, context):
		"""
		Handles the logic when the user confirms the popup.

		Simply continues processing; used when "Continue" is clicked.
		Returns {'FINISHED'} to complete the operator.
		"""

		return {'FINISHED'}  # Continue

	def invoke(self, context, event):
		"""
		Displays the popup window for the debug prompt.

		Sets up and invokes the popup layout using Blender's window manager.
		Called automatically when the operator is invoked in the UI.
		"""

		wm = context.window_manager
		return wm.invoke_popup(self, width=500)  # Wider than default

	def draw(self, context):
		"""
		Draws the content of the debug popup window.

		Displays each line of the message as a label, and provides Continue/Cancel buttons.
		Used during popup UI rendering.
		"""

		layout = self.layout
		col = layout.column()
		for line in self.message.split("\n"):
			col.label(text=line)
		col.separator()
		row = col.row()
		row.operator("asset.debug_continue", text="Continue")
		row.operator("asset.debug_cancel", text="Cancel")

class ASSET_OT_DebugContinue(bpy.types.Operator):
	"""
	Operator that continues processing after a debug warning.

	Used when the user confirms they want to proceed despite complex materials.
	Prints confirmation to the console and completes normally.
	"""

	bl_idname = "asset.debug_continue"
	bl_label = "Continue Processing"

	def execute(self, context):
		"""
		Handles confirmation logic when user chooses to continue.

		Prints a debug message and returns {'FINISHED'} to resume processing.
		"""

		print("[INFO] User chose to continue after debug prompt.")
		return {'FINISHED'}

class ASSET_OT_DebugCancel(bpy.types.Operator):
	"""
	Operator that cancels processing after a debug warning.

	Used when the user chooses to stop after being warned about complex materials.
	Reports the cancellation and exits the operator with {'CANCELLED'}.
	"""

	bl_idname = "asset.debug_cancel"
	bl_label = "Cancel Processing"

	def execute(self, context):
		"""
		Handles cancellation logic when user stops processing.

		Reports a warning to the user and returns {'CANCELLED'} to stop further execution.
		"""

		self.report({'WARNING'}, "Processing cancelled by user from summary popup.")
		return {'CANCELLED'}
	
def register_debug_operators():
	"""
	Registers the debug-related popup operators with Blender.

	This function is called in the main addon register() method.
	Allows debug prompts to be used in the UI or invoked manually.
	"""

	bpy.utils.register_class(ASSET_OT_DebugPrompt)
	bpy.utils.register_class(ASSET_OT_DebugContinue)
	bpy.utils.register_class(ASSET_OT_DebugCancel)

def unregister_debug_operators():
	"""
	Unregisters the debug-related popup operators from Blender.

	Called during addon shutdown or reload to clean up operator classes.
	Ensures no stale operators remain in memory.
	"""

	bpy.utils.unregister_class(ASSET_OT_DebugPrompt)
	bpy.utils.unregister_class(ASSET_OT_DebugCancel)
	bpy.utils.unregister_class(ASSET_OT_DebugContinue)
