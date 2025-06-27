from allensdk.core.reference_space_cache import ReferenceSpaceCache

resolution = 25
rspc = ReferenceSpaceCache(resolution=resolution, reference_space_key='ccf_2017')
reference_space = rspc.get_reference_space()

root_id = reference_space.get_structure_tree().root_id
root_struct = reference_space.get_structure_tree().get_structures_by_id(root_id)[0]

print(f"Loaded atlas root ID: {root_id}")
print(f"Loaded atlas root name: {root_struct['name']}")

whole_brain_mesh = reference_space.get_mesh(root_id)
whole_brain_mesh.export('whole_brain.stl')

print("Exported whole brain STL!")
