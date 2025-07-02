import trimesh

# Load your STL file
mesh = trimesh.load_mesh("EIB16MouseImplant.stl")

# Volume in mm³
volume_mm3 = mesh.volume
# Convert to cm³
volume_cm3 = volume_mm3 / 1000

# Resin density (example: 1.12 g/cm³)
density = 1.12  # g/cm³
weight = volume_cm3 * density

print(f"Volume: {volume_cm3:.2f} cm³")
print(f"Estimated weight: {weight:.2f} g")
