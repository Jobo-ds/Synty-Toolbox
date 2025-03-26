import bpy
import os

def get_files_in_folder(folder_path, ext):
	"""
	Finds all files in the given folder path of a certain ext.

	Scans the directory for files ending in .ext (case-insensitive).
	Returns a list of full file paths.
	"""

	try:
		fbx_files = [
			os.path.join(folder_path, f)
			for f in os.listdir(folder_path)
			if f.lower().endswith(f".{ext}") and os.path.isfile(os.path.join(folder_path, f))
		]
		print(f"[INFO] Found {len(fbx_files)} {ext} file(s) in folder: {folder_path}")
		return fbx_files
	except Exception as e:
		print(f"[ERROR] Failed to list files: {e}")
		return []
	
	