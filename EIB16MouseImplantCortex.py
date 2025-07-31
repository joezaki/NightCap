import subprocess
import math

openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"  # Use forward slashes

# Define all electrode entrances
A1 = [-4.2,0.36,4.75]
A2 = [-4.2,1.49,4.75]
A3 = [-4.2, 2.62,4.75]
A4 = [-4.2, 3.75,4.75]
A5 = [-2.05,4.15,4.75]
A6 = [-0.92,4.15,4.75]
A7 = [0.21,4.15,4.75]
A8 = [1.34,4.15,4.75]
A9 = [4.2,-0.36,4.75]
A10 = [4.2,-1.49,4.75]
A11 = [4.2,-2.62,4.75]
A12 = [4.2,-3.75,4.75]
B1 = [2.05,-4.15,4.75]
B2 = [0.92,-4.15,4.75]
B3 = [-0.21,-4.15,4.75]
B4 = [-1.34,-4.15,4.75]


A9Ground = [4.15,1.14, 4.75]
A1Ground = [-4.15,-1.14,4.75]

# Brain Regions (ML, AP, DV) up to 12
Region1 = [0.4, 2.2, -2.5]
Region2 = [-0.4, 2.2, -2.5]
Region3 = [1.5, 1.2, -1.5]
Region4 = [-1.5, 1.2, -1.5]
Region5 = [ 3, -1, -1.8]
Region6 = [-3,-1, -1.8]
Region7 = [1.5,-2.7, -0.8]
Region8 = [-1.5, -2.7, -0.8]
Region9 = [2.5, -3.5, -1.2]
Region10 = [-2.5, -3.5, -1.2]
Region11 = [4, -2.5, -2.2]
Region12 = [-4, -2.5, -2.2]
Region13 = [1.3, -1.8, -1.5]  
Region14 = [-1.3, -1.8, -1.5]
Region15 = [0.5, -1.2, -3]
Region16 = [-0.5,-1.2, -3]
            
Region1_updated = [Region1[0], Region1[1] + 2,Region1[2]]
Region2_updated = [Region2[0], Region2[1] + 2, Region2[2]]
Region3_updated = [Region3[0], Region3[1] + 2, Region3[2]]
Region4_updated = [Region4[0], Region4[1] + 2, Region4[2]]
Region5_updated = [Region5[0], Region5[1] + 2, Region5[2]]
Region6_updated = [Region6[0], Region6[1] + 2, Region6[2]]
Region7_updated = [Region7[0], Region7[1] + 2, Region7[2]]
Region8_updated = [Region8[0], Region8[1] + 2, Region8[2]]
Region9_updated = [Region9[0], Region9[1] + 2, Region9[2]]
Region10_updated = [Region10[0], Region10[1] + 2, Region10[2]]
Region11_updated = [Region11[0], Region11[1] + 2, Region11[2]]
Region12_updated = [Region12[0], Region12[1] + 2, Region12[2]]
Region13_updated = [Region13[0], Region13[1] + 2, Region13[2]]
Region14_updated = [Region14[0], Region14[1] + 2, Region14[2]]
Region15_updated = [Region15[0], Region15[1] + 2, Region15[2]]
Region16_updated = [Region16[0], Region16[1] + 2, Region16[2]]

#Ground Regions
GroundRegion1 = [-1, -5.5, -1.5]
GroundRegion2 = [-0.3, 2.2, -2.5]

GroundRegion1_updated = [GroundRegion1[0], GroundRegion1[1] + 2, GroundRegion1[2]]
GroundRegion2_updated = [GroundRegion2[0], GroundRegion2[1] + 2, GroundRegion2[2]]




# List of holes: (entry_point_xyz, exit_point_xyz)

holes = [
    (A7, Region1_updated),(A6, Region2_updated) ,(A8, Region3_updated) , (A5, Region4_updated),(A9, Region5_updated),
    (A4, Region6_updated), (B1, Region7_updated), (B4, Region8_updated), (A12, Region9_updated), (A1, Region10_updated),
    (A10, Region11_updated), (A3, Region12_updated), (A11, Region13_updated), (A2, Region14_updated),
    (B2, Region15_updated), (B3, Region16_updated)
]
ground_holes = [ (A1Ground, GroundRegion1_updated)
    ]

hole_radius = 0.34
ground_radius = 0.4
desired_exit_z = 1.5  # Desired Z coordinate for the exit point
stl_file = "BlankMouseImplantv3.stl"

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
    adjusted_exit = [exit[0], exit[1], desired_exit_z]
    vec = vec_sub(adjusted_exit, entry)
    length = vec_len(vec)
    unit_vec = normalize(vec)
    extra = 0.11
    base_point = [exit[i] for i in range(3)]
    height = desired_exit_z
    base_point = [exit[i] + unit_vec[i] * extra for i in range(3)]
    height = desired_exit_z 
    height_z = desired_exit_z + 0.25 
    angle = angle_between(vec)
    axis = rotation_axis(vec)
    angle, axis = flip_angle_axis(angle, axis, vec)

    scad_code += f"""// Hole from {entry} to {exit}
translate([{base_point[0]:.4f}, {base_point[1]:.4f}, {height:.4f}])
rotate(a = {angle:.4f}, v = [{axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f}])
    cylinder(h = {length + 1.2:.4f}, r = {hole_radius}, $fn=60);
translate([{exit[0]:.4f}, {exit[1]:.4f}, 0])
        cylinder(h = {height_z}, r = {hole_radius}, $fn=60);
"""
    
for entry_g, exit_g in ground_holes:
    adjusted_exit_g = [exit_g[0], exit_g[1], desired_exit_z]
    vec_g = vec_sub(adjusted_exit_g, entry_g)
    length_g = vec_len(vec_g)
    unit_vec_g = normalize(vec_g)
    extra_g = 0.11
    base_point_g = [exit_g[i] for i in range(3)]
    height_g = desired_exit_z 
    height_z = desired_exit_z + 0.2 
    base_point_g = [exit_g[i] + unit_vec_g[i] * extra_g for i in range(3)]
    height = desired_exit_z 
    height_z_g = desired_exit_z + 0.232 
    angle_g = angle_between(vec_g)
    axis_g = rotation_axis(vec_g)
    angle_g, axis_g = flip_angle_axis(angle_g, axis_g, vec_g)

    scad_code += f"""// Ground hole from {entry_g} to {exit_g}
translate([{base_point_g[0]:.4f}, {base_point_g[1]:.4f}, {height_g:.4f}])
rotate(a = {angle_g:.4f}, v = [{axis_g[0]:.4f}, {axis_g[1]:.4f}, {axis_g[2]:.4f}])
    cylinder(h = {length_g + 1.2:.4f}, r = {ground_radius}, $fn=60);
translate([{exit_g[0]:.4f}, {exit_g[1]:.4f}, 0])
    cylinder(h = {height_z_g}, r = {ground_radius}, $fn=60);
"""
    
final_scad = f"""
difference() {{
{scad_code}
}}
"""

with open("EIB16MouseImplantCortex.scad", "w") as f:
    f.write(final_scad)

result = subprocess.run([
    openscad_path,
    "-o", "ImplantTestCortex_73125.stl",
    "EIB16MouseImplantCortex.scad"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ EIB16MouseImplantCompleted.stl generated successfully!")

outer_radius = 0.5
inner_radius = 0.28
outer_radius_g = 0.6
inner_radius_g = 0.3
depth_guide_scad = ""
for i, (entry, exit) in enumerate(holes):
    if i % 2 == 0:
        height_depth = -exit[2]
        depth_guide_scad += f"""
difference() {{
    translate([{0.7*i}, {0}, {exit[2]:.4f}])
        cylinder(h = {height_depth}, r = {outer_radius}, $fn=60);

    translate([{0.7*i}, {0}, {exit[2]:.4f}])
        cylinder(h = {height_depth}, r = {inner_radius}, $fn=60);
}}
"""

for i, (entry, exit) in enumerate(ground_holes):
    height_depth_g = -exit[2]
    depth_guide_scad += f"""
    difference() {{
        translate([{i}, {2}, {exit[2]:.4f}])
            cylinder(h = {height_depth_g}, r = {outer_radius_g}, $fn=60);

        translate([{i}, {2}, {exit[2]:.4f}])
            cylinder(h = {height_depth_g}, r = {inner_radius_g}, $fn=60);
}}
"""
final_depth_guide_scad = f"""

{depth_guide_scad}

"""
# Write .scad file for wire depth guide
with open("DepthGuideCortex.scad", "w") as f:
    f.write(final_depth_guide_scad)

# Render STL for wire depth guide
result2 = subprocess.run([
    openscad_path,
    "-o", "DepthTestCortex_73125.stl",
    "DepthGuideCortex.scad"
], capture_output=True, text=True)

if result2.returncode != 0:
    print("❌ Error running OpenSCAD on DepthGuide:")
    print(result2.stderr)
else:
    print("✅ DepthGuide.stl generated successfully!")