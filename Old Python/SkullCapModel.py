import subprocess
import os

# STEP 1: Path to OpenSCAD
openscad_path = r"C:/Program Files/OpenSCAD/openscad.exe"  # Make sure this is correct

# STEP 2: Parameters
hole_coords = [(1, 2), (2, 3), (2.5, 3.1)]
hole_radius = 0.5
plate_height = 2

# STEP 3: SCAD code
scad_code = f"""
difference() {{
    // Base plate for surgical guide
    translate([-10, -10, 0])
        cube([20, 20, {plate_height}], center=false);

    // Electrode holes
"""

for x, y in hole_coords:
    scad_code += f"    translate([{x}, {y}, -1]) cylinder(h = 10, r = {hole_radius}, $fn=50);\n"

scad_code += "}\n"  # closes difference block

# Optional: Add skull STL for visualization (does not affect output shape)
scad_code += """
// Skull model (not part of difference)
translate([-15.3, -14.00, 1])
rotate([-1.4, 90, 0])
    import("files/Mouse_Skull.stl");
"""

# STEP 4: Write SCAD file
with open("SkullCap.scad", "w") as f:
    f.write(scad_code)

# STEP 5: Run OpenSCAD to generate STL
result = subprocess.run([
    openscad_path,
    "-o", "SkullCap.stl",
    "SkullCap.scad"
], capture_output=True, text=True)

# STEP 6: Output result
if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
else:
    print("✅ SkullCap.stl generated successfully!")
