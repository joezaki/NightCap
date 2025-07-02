import subprocess
import math

openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"  # Use forward slashes

# Define all electrode entrances
A1 = [-4.2,0.36,3.75]
A2 = [-4.2,1.49,3.75]
A3 = [-4.2, 2.62,3.75]
A4 = [-4.2, 3.75,3.75]
A5 = [-2.05,4.15,3.75]
A6 = [-0.92,4.15,3.75]
A7 = [0.21,4.15,3.75]
A8 = [1.34,4.15,3.75]
A9 = [4.2,-0.36, 3.75]
A10 = [4.2,-1.49,3.75]
A11 = [4.2,-2.62,3.75]
A12 = [4.2,-3.75,3.75]
B1 = [2.05,-4.15,3.75]
B2 = [0.92,-4.15,3.75]
B3 = [-0.21,-4.15,3.75]
B4 = [-1.34,-4.15,3.75]
# Brain Regions (ML, AP, DV)
Region1 = [0.3, 2.2, -2.5]
Region2 = [-0.3, 2.2, -2.5]
Region3 = [1.3, -2.0, -1.5]
Region4 = [-1.3, -2.0, -1.5]
Region5 = [ 2, 0.5, -3.5]
Region6 = [-2,0.5, -3.5]
Region7 = [1,-5.5, -2]
Region8 = [-1, -5.5, -2]
Region9 = [1, 5, -1]
Region10 = [-4, 6, 0]
Region11 = [3, -2, 4]
Region12 = [2, 4, -3]

Region1_updated = [Region1[0], Region1[1] + 2, 1]
Region2_updated = [Region2[0], Region2[1] + 2, 1]
Region3_updated = [Region3[0], Region3[1] + 2, 1]
Region4_updated = [Region4[0], Region4[1] + 2, 1]
Region5_updated = [Region5[0], Region5[1] + 2, 1]
Region6_updated = [Region6[0], Region6[1] + 2, 1]
Region7_updated = [Region7[0], Region7[1] + 2, 1]
Region8_updated = [Region8[0], Region8[1] + 2, 1]
Region9_updated = [Region9[0], Region9[1] + 2, 1]
Region10_updated = [Region10[0], Region10[1] + 2, 1]
Region11_updated = [Region11[0], Region11[1] + 2, 1]
Region12_updated = [Region12[0], Region12[1] + 2, 1]


# List of holes: (entry_point_xyz, exit_point_xyz)
holes = [
    (A9, Region3_updated), (A1, Region4_updated), (A7, Region1_updated), (A6, Region2_updated),(A8, Region5_updated),
    (A5, Region6_updated), (B2, Region7_updated), (B3, Region8_updated), 
]

hole_radius = 0.23
stl_file = "BlankMouseImplant.stl"

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

for entry, exit in holes:
    # Vector from entry to exit
    vec = vec_sub(exit, entry)
    length = vec_len(vec)
    unit_vec = normalize(vec)
    extra = 0.2
    base_point = [exit[i] + unit_vec[i] * extra for i in range(3)]

    angle = angle_between(vec)
    axis = rotation_axis(vec)
    angle, axis = flip_angle_axis(angle, axis, vec)

    scad_code += f"""// Hole from {entry} to {exit}
translate([{base_point[0]:.4f}, {base_point[1]:.4f}, {base_point[2]:.4f}])
rotate(a = {angle:.4f}, v = [{axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f}])
    cylinder(h = {length + 1.2:.4f}, r = {hole_radius}, $fn=60);
translate([{exit[0]:.4f}, {exit[1]:.4f}, 0])
        cylinder(h = 1, r = {hole_radius}+0.05, $fn=60);
"""

final_scad = f"""
difference() {{
{scad_code}
}}
"""

with open("EIB16MouseImplant.scad", "w") as f:
    f.write(final_scad)

result = subprocess.run([
    openscad_path,
    "-o", "EIB16MouseImplant.stl",
    "model2.scad"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ EIB16MouseImplant.stl generated successfully!")
