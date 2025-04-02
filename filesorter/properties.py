import bpy
from bpy.props import StringProperty
from bpy.types import PropertyGroup


class SSTOOL_PG_FileSorterProperties(PropertyGroup):

	sort_folder: StringProperty(
		name="Input Folder",
		description="Folder containing FBX files to sort into folders",
		subtype='DIR_PATH',
	) # type: ignore	