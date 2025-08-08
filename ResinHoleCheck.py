import subprocess
import math

openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"  # Use forward slashes

hole_radius = 0.28
ground_radius = 0.4
desired_exit_z = 0.5  # Desired Z coordinate for the exit point
stl_file = "HoleCheckBlankv3.stl"

def vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]

def vec_len(v):
    return math.sqrt(sum(x*x for x in v))

def normalize(v):
    length = vec_len(v)
    return [x/length for x in v]

def dot_product(a, b):
    return sum(a[i]*b[i] for i in range(3))

def cross_product(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]

def angle_between(v):
    v_norm = normalize(v)
    dot = max(min(v_norm[2], 1.0), -1.0)  # Clamp dot between -1 and 1
    angle = math.acos(dot) * 180 / math.pi
    return angle

def rotation_axis(v):
    v_norm = normalize(v)
    axis = cross_product([0,0,1], v_norm)
    length = vec_len(axis)
    if length < 1e-8:
        return [1, 0, 0]
    return [x/length for x in axis]

def flip_angle_axis(angle, axis, v):
    v_norm = normalize(v)
    dot = v_norm[2]
    if dot < 0:
        return 180 - angle, [-x for x in axis]
    else:
        return angle, axis

scad_code = f"// Import your STL model\nimport(\"{stl_file}\");\n\n"

for i in range(0, 9):
    entry_check = [6.5,6-(1.5*i),4.75]
    check_radius = 0.1+0.01*i
    scad_code += f"""
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 5, r = {check_radius}, $fn=60);
"""
for i in range(0, 9):
    entry_check = [5.3,6-(1.5*i),4.75]
    check_radius = 0.2+0.01*i
    scad_code += f"""
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 5, r = {check_radius}, $fn=60);
"""
for i in range(0, 9):
    entry_check = [4.1,6-(1.5*i),4.75]
    check_radius = 0.3+0.01*i
    scad_code += f"""
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 5, r = {check_radius}, $fn=60);
"""    
for i in range(0, 9):
    entry_check = [2.9,6-(1.5*i),4.75]
    check_radius = 0.1+0.01*i
    scad_code += f"""
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 5, r = {check_radius}, $fn=60);
"""
for i in range(0, 9):
    entry_check = [1.7,6-(1.5*i),4.75]
    check_radius = 0.2+0.01*i
    scad_code += f"""
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 5, r = {check_radius}, $fn=60);
"""
for i in range(0, 9):
    entry_check = [0.5,6-(1.5*i),4.75]
    check_radius = 0.3+0.01*i
    scad_code += f"""
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 5, r = {check_radius}, $fn=60);
"""    
    
      
final_scad = f"""
difference() {{
{scad_code}
}}
"""

with open("HoleCheck.scad", "w") as f:
    f.write(final_scad)

result = subprocess.run([
    openscad_path,
    "-o", "HoleCheck8725.stl",
    "HoleCheck.scad"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ HoleCheck.stl generated successfully!")
