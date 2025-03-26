import bpy
import os

def create_output_folder(folder_name):
	"""
	Creates an output folder inside the input directory.

	Uses the name of the input folder to generate a subdirectory for exported files.
	Returns the path if successful, or None on error.
	"""

	try:
		base_name = os.path.basename(os.path.normpath(folder_name))
		output_folder = os.path.join(folder_name, base_name)

		if not os.path.exists(output_folder):
			os.makedirs(output_folder)
			print(f"[INFO] Created output folder: {output_folder}")
		else:
			print(f"[INFO] Output folder already exists: {output_folder}")

		return output_folder
	except Exception as e:
		print(f"[ERROR] Failed to create output folder: {e}")
		return None
	
def get_subfolders(folder_path, ext):
	"""
	Finds all subfolders (recursively) within folder_path that contain files with the given extension.

	Returns a list of full folder paths.
	"""
	matching_folders = []

	try:
		for root, _, files in os.walk(folder_path):
			if any(f.lower().endswith(f".{ext}") for f in files):
				matching_folders.append(root)

		print(f"[INFO] Found {len(matching_folders)} folders containing .{ext} files.")
		return matching_folders

	except Exception as e:
		print(f"[ERROR] Failed to search folders: {e}")
		return []