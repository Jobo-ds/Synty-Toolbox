# ReadMe
This is a plugin I made for myself to work with Synty assets.

It can:

- Convert FBX -> GLB
- Convert GLB -> Blend
- Auto sort into folders.

# How to use
Install plugin to Blender.

Create a folder hierachy like this: (Names doesn't matter)

- _conv
  - Root
  - Characters
  - Output

1. Copy all the FBX files from the FBX folder into "Root".
2. In Blender, use the "Auto Sort" on the "Root" folder.
   - Now you have a folder full of category folders. If any ended up in odd folders, just move them around to your liking.
3. From the texture folder, copy a texture (and optionally a normal, if there is one) into each folder.
   - This texture/normal will be added to every FBX file in the folder.
   - You may need to create more subfolders if there are specific textures for specific files, like "Billboard" or "Road".
4. In Blender, use the FBX to GLB converter on the "Root" folder and output to the "Output" folder.
   - There are some optional settings. Use them as needed.
5. In Blender, use the FBX to GLB converter on the "Character" folder, optionally use the "Rotate characters" setting.
   - Please keep in mind that no guarantees are made for how Characters are setup. I don't know anything about that.

Done!
