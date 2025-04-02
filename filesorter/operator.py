import bpy
import os
import shutil

TOKEN_TO_FOLDER = {
	"Bld": "Buildings",
	"Wep": "Weapons",
	"Env": "Environment",
	"Veh": "Vehicles",
	"FX": "Effects",
	"Particle": "Effects",
}

def get_category_from_name(filename):
	name = filename.lower()
	parts = filename.split("_")

	# Priority 1: Demo
	if "demo" in name:
		return "Demo"

	# Priority 2: Explicit "character" keyword
	if "character" in name:
		return "Characters"

	# Priority 3: Character attachments
	if "_attach_" in name and ("_chr_" in name or "_char_" in name or name.startswith("character_")):
		return "Character Attachments"

	# Priority 4: Use first token if it's a known category
	if len(parts) >= 1 and parts[0] in TOKEN_TO_FOLDER:
		return TOKEN_TO_FOLDER[parts[0]]

	# Priority 5: If first token isn't useful, check second token
	if len(parts) >= 2 and parts[1] in TOKEN_TO_FOLDER:
		return TOKEN_TO_FOLDER[parts[1]]

	# Priority 6: Unknown second token (fallback to capitalized name)
	if len(parts) >= 2:
		return parts[1].capitalize()

	# Priority 7: Fallback to first part, capitalized
	return "Others"



class SSTOOL_OT_SortFilesOperator(bpy.types.Operator):
	bl_idname = "sstool.sort_files_to_folders"
	bl_label = "Auto Sort Files by Name"
	bl_description = "Sorts FBX files into folders based on naming conventions"

	def execute(self, context):
		folder = context.scene.filesorter_props
		if not os.path.isdir(folder):
			self.report({'ERROR'}, "Invalid FBX folder.")
			return {'CANCELLED'}

		for filename in os.listdir(folder):
			filepath = os.path.join(folder, filename)
			if not os.path.isfile(filepath) or not filename.lower().endswith(".fbx"):
				continue

			category = get_category_from_name(filename)

			# Fallback: if category == filename (without extension), send to "Others"
			name_without_ext = os.path.splitext(filename)[0]
			if category.lower() == name_without_ext.lower():
				category = "Others"

			target_folder = os.path.join(folder, category)

			# Avoid folder/file name conflict
			if os.path.isfile(target_folder):
				self.report({'WARNING'}, f"Skipped {filename}: a file named '{category}' already exists.")
				continue

			os.makedirs(target_folder, exist_ok=True)

			try:
				shutil.move(filepath, os.path.join(target_folder, filename))
			except Exception as e:
				self.report({'WARNING'}, f"Failed to move {filename}: {e}")

		self.report({'INFO'}, "FBX files sorted successfully.")
		return {'FINISHED'}