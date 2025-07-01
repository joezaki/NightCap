import subprocess

openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"  # Use forward slashes

hole_coords = [(1, 2), (2, 3), (2.5, 3.1)]
hole_radius = 0.5
plate_radius = 5
plate_height = 2

scad_code = f"""
// Import mouse skull
translate([-15.3, -14.00, 1]) {{
    rotate([-1.4, 90, 0])
        import("files/Mouse_Skull.stl");
}}

// Load your STL
translate([0, 0, 1]) {{
    import("MouseBoxEIB16.stl");
}}

// Electrode holes
"""

with open("model.scad", "w") as f:
    f.write(scad_code)

result = subprocess.run([
    openscad_path,
    "-o", "model.stl",
    "model.scad"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ model.stl generated successfully!")
