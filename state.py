import bpy

# state.py

# List of (material_name, object_name, node_count) for materials with complex node setups.
# Populated during processing if a material exceeds a certain threshold of nodes.
# Used to trigger debug popups or warnings after processing.

flagged_complex_materials = []

# Counter used to generate unique names for new materials.
# Increments with each created material to avoid naming conflicts.
# Resets after a full processing batch completes.

generated_material_counter = 1
