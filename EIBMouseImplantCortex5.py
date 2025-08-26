
import subprocess
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import os

output_folder = "Generated Files"
os.makedirs(output_folder, exist_ok=True)
scad_folder = "SCAD Files"
os.makedirs(scad_folder, exist_ok=True)
openscad_path = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD" #Update this path as needed
ImplantName = "EIB16MouseImplantCortex_82525"
DepthGuideName = "EIB16DepthGuideCortex_82525"

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

implant_boundary = [
    (0, -5), 
    (2.6, -4.4), 
    (4.6, -3.2), 
    (5.2, -2.2),
    (5.2, 0.6),  
    (4.4, 2.8), 
    (3.2, 4.4), 
    (0, 6), 
    (-3.2, 4.2), 
    (-4.5, 2.6), 
    (-5.2, 0.6), 
    (-5.2, -2.2), 
    (-4.6, -3.2), 
    (-2.6, -4.4),
]

# List of holes: (entry_point_xyz, exit_point_xyz)

holes = [
    (A7, Region1_updated),(A6, Region2_updated) ,(A8, Region3_updated) , (A5, Region4_updated),(A9, Region5_updated),
    (A4, Region6_updated), (B1, Region7_updated), (B4, Region8_updated), (A12, Region9_updated), (A1, Region10_updated),
    (A10, Region11_updated), (A3, Region12_updated), (A11, Region13_updated), (A2, Region14_updated),
    (B2, Region15_updated), (B3, Region16_updated)
]
holes_dict = {
    "A7":  (A7,  Region1_updated),
    "A6":  (A6,  Region2_updated),
    "A8":  (A8,  Region3_updated),
    "A5":  (A5,  Region4_updated),
    "A9":  (A9,  Region5_updated),
    "A4":  (A4,  Region6_updated),
    "B1":  (B1,  Region7_updated),
    "B4":  (B4,  Region8_updated),
    "A12": (A12, Region9_updated),
    "A1":  (A1,  Region10_updated),
    "A10": (A10, Region11_updated),
    "A3":  (A3,  Region12_updated),
    "A11": (A11, Region13_updated),
    "A2":  (A2,  Region14_updated),
    "B2":  (B2,  Region15_updated),
    "B3":  (B3,  Region16_updated),
    "GNDA1": (A1Ground, GroundRegion1_updated),
}

hole_radius = 0.27
stl_file = "BlankMouseImplantShapedv4.stl"
stl2_file = "BlankDepthGuideShapedv4.stl"
hole_labels = [label for (label, _) in holes]
hole_positions = [exit for (_, exit) in holes_dict.values()]
label_radius = 1  # Collision radius for label placement
label_size = 0.25


def vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def draw_implant_visual(implant_boundary, hole_positions, output_file="implant_visual.pdf"):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    
    # Plot implant boundary
    boundary_polygon = Polygon(implant_boundary, closed=True, edgecolor='black', fill=False, linewidth=1.5)
    ax.add_patch(boundary_polygon)

    # Plot holes and labels
    for label, (_, (x, y, z)) in holes_dict.items():
        circle = Circle((x, y), radius=0.4, color='black', fill=False, linewidth=1)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=6)

    # Adjust limits
    all_x = [x for (x, y, z) in hole_positions]
    all_y = [y for (x, y, z) in hole_positions]
    ax.set_xlim(min(all_x) - 2, max(all_x) + 2)
    ax.set_ylim(min(all_y) - 2, max(all_y) + 2)

    ax.axis('off')  # Hide axes
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


scad_code = f"// Import your STL model\nimport(\"{stl_file}\");\n\n"

for label, (entry, exit) in holes_dict.items():
    # Vector from entry to exit
    adjusted_exit = [exit[0], exit[1], 0]
    if label.upper().startswith("GND"):
        r = hole_radius + 0.1  
    else:
        r = hole_radius  


    scad_code += f"""// Hole from {entry} to {exit}
translate([{exit[0]:.4f}, {exit[1]:.4f}, 0])
        cylinder(h = {5}, r = {r}, $fn=60);
"""

final_scad = f"""
difference() {{
{scad_code}
}}
"""

implant_scad_path = os.path.join(scad_folder, "EIB16MouseImplantCortex.scad")
with open(implant_scad_path, "w") as f:
    f.write(final_scad)

implant_stl_path = os.path.join(output_folder, f"{ImplantName}.stl")

result = subprocess.run([
    openscad_path,
    "-o", implant_stl_path,
    implant_scad_path
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ EIB16MouseImplantCompleted.stl generated successfully!")


depth_guide_scad = f'import("{stl2_file}");\n\n'
depth_guide_scad1 = ''
depth_guide_scad2 = ''
outer_radius = 0.6
inner_radius = 0.27
for label, (entry, exit) in holes_dict.items():
    if label.upper().startswith("GND"):
        r = outer_radius + 0.1
    else:
        r = outer_radius  
    height_depth = -exit[2]
    depth_guide_scad1 += f"""
    translate([{exit[0]}, {exit[1]}, {exit[2]:.4f}])
        cylinder(h = {height_depth:.4f}, r = {r}, $fn=60);
"""

for label, (entry, exit) in holes_dict.items():
    if label.upper().startswith("GND"):
        r = inner_radius + 0.1
    else:
        r = inner_radius
    height_depth = -exit[2]
    depth_guide_scad2 += f"""
    translate([{exit[0]}, {exit[1]}, {exit[2]:.4f}])
        cylinder(h = {height_depth:.4f}, r = {r}, $fn=60);
"""

# Final SCAD: difference of outer – inner
final_depth_guide_scad = f"""
difference() {{
    union() {{
{depth_guide_scad}
{depth_guide_scad1}
    }}
{depth_guide_scad2}
}}

"""

depth_scad_path = os.path.join(scad_folder, "DepthGuideCortex.scad")
with open(depth_scad_path, "w") as f:
    f.write(final_depth_guide_scad)

depth_stl_path = os.path.join(output_folder, f"{DepthGuideName}.stl")

result2 = subprocess.run([
    openscad_path,
    "-o", depth_stl_path,
    depth_scad_path
], capture_output=True, text=True)

if result2.returncode != 0:
    print("❌ Error running OpenSCAD on DepthGuide:")
    print(result2.stderr)
else:
    print("✅ DepthGuide.stl generated successfully!")

pdf_path = os.path.join(output_folder, "implant_visual.pdf")
draw_implant_visual(implant_boundary, hole_positions, output_file=pdf_path)
print("✅ implant_visual.pdf generated successfully!")
