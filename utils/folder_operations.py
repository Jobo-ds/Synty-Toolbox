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