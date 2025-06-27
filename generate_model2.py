import subprocess
import math

openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"  # Use forward slashes

# List of holes: (entry_point_xyz, exit_point_xyz)
holes = [
    ([1.58, 4.2, 3.75], [2, 2, 0]), ([4.2, -0.9, 3.75], [2, -2, 0]), ([2, -4.2, 3.75], [1.5, -3.2, 0]),
]

hole_radius = 0.4
stl_file = "MouseBox3_v2.stl"

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
    extra = 1
    base_point = [exit[i] + unit_vec[i] * extra for i in range(3)]

    angle = angle_between(vec)
    axis = rotation_axis(vec)
    angle, axis = flip_angle_axis(angle, axis, vec)

    scad_code += f"""// Hole from {entry} to {exit}
translate([{base_point[0]:.4f}, {base_point[1]:.4f}, {base_point[2]:.4f}])
rotate(a = {angle:.4f}, v = [{axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f}])
    cylinder(h = {length + 1.2:.4f}, r = {hole_radius}, $fn=60);
"""

final_scad = f"""
difference() {{
{scad_code}
}}
"""

with open("model2.scad", "w") as f:
    f.write(final_scad)

result = subprocess.run([
    openscad_path,
    "-o", "model2.stl",
    "model2.scad"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ model2.stl generated successfully!")
