import bpy

# state.py

# Counter used to generate unique names for new materials.
# Increments with each created material to avoid naming conflicts.
# Resets after a full processing batch completes.

generated_material_counter = 1
