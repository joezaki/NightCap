import subprocess
import math

openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"  # Use forward slashes

hole_radius = 0.28
ground_radius = 0.4
desired_exit_z = 0.5  # Desired Z coordinate for the exit point
stl_file = "HoleCheckBlank.stl"

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
    entry_check = [6,6-(1.5*i),3.75]
    exit_check = [6,6-(1.5*i),0]
    check_radius = 0.1+0.06*i
    scad_code += f"""// Hole check from {entry_check} to {exit_check}
translate([{entry_check[0]:.4f}, {entry_check[1]:.4f}, 0])
    cylinder(h = 3.75, r = {check_radius}, $fn=60);
"""
    

for i in range(0, 6):
   # Vector from entry to exit
    entry_check2 = [4,6-(1*i),3.75]
    exit_check2 = [4,6-(2*i),desired_exit_z]
    hole_radius2 = 0.28
    vec = vec_sub(exit_check2, entry_check2)
    length = vec_len(vec)
    unit_vec = normalize(vec)
    extra = 0.2
    base_point = [exit_check2[i] for i in range(3)]
    height = desired_exit_z 
    angle = angle_between(vec)
    axis = rotation_axis(vec)
    angle, axis = flip_angle_axis(angle, axis, vec)

    scad_code += f"""// Hole from {entry_check2} to {exit_check2}
translate([{base_point[0]:.4f}, {base_point[1]:.4f}, {height:.4f}])
rotate(a = {angle:.4f}, v = [{axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f}])
    cylinder(h = {length + 1.2:.4f}, r = {hole_radius2}, $fn=60);
translate([{exit_check2[0]:.4f}, {exit_check2[1]:.4f}, 0])
        cylinder(h = {desired_exit_z}+0.2, r = {hole_radius2}, $fn=60);
"""
for i in range(0, 6):
   # Vector from entry to exit
    entry_check3 = [2,6-(1*i),3.75]
    exit_check3 = [2,6-(2*i),desired_exit_z]
    hole_radius3 = 0.23
    vec = vec_sub(exit_check3, entry_check3)
    length = vec_len(vec)
    unit_vec = normalize(vec)
    extra = 0.2
    base_point = [exit_check3[i] + unit_vec[i] * extra for i in range(3)]
    height = desired_exit_z + unit_vec[2] * extra
    angle = angle_between(vec)
    axis = rotation_axis(vec)
    angle, axis = flip_angle_axis(angle, axis, vec)

    scad_code += f"""// Hole from {entry_check3} to {exit_check3}
translate([{base_point[0]:.4f}, {base_point[1]:.4f}, {height:.4f}])
rotate(a = {angle:.4f}, v = [{axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f}])
    cylinder(h = {length + 1.2:.4f}, r = {hole_radius3}, $fn=60);
translate([{exit_check3[0]:.4f}, {exit_check3[1]:.4f}, 0])
        cylinder(h = {desired_exit_z}, r = {hole_radius3}+0.05, $fn=60);
"""

for i in range(0, 6):
   # Vector from entry to exit
    entry_check4 = [0,6-(i*1.5),3.75]
    exit_check4 = [0,3-(i*1.5),desired_exit_z]
    hole_radius4 = 0.1+0.06*i
    vec = vec_sub(exit_check4, entry_check4)
    length = vec_len(vec)
    unit_vec = normalize(vec)
    extra = 0.2
    base_point = [exit_check4[i] for i in range(3)]
    height = desired_exit_z 
    angle = angle_between(vec)
    axis = rotation_axis(vec)
    angle, axis = flip_angle_axis(angle, axis, vec)

    scad_code += f"""// Hole from {entry_check4} to {exit_check4}
translate([{base_point[0]:.4f}, {base_point[1]:.4f}, {height:.4f}])
rotate(a = {angle:.4f}, v = [{axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f}])
    cylinder(h = {length + 1.2:.4f}, r = {hole_radius4}, $fn=60);
translate([{exit_check4[0]:.4f}, {exit_check4[1]:.4f}, 0])
        cylinder(h = {desired_exit_z}+0.2, r = {hole_radius4}, $fn=60);
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
    "-o", "HoleCheck.stl",
    "HoleCheck.scad"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ HoleCheck.stl generated successfully!")
