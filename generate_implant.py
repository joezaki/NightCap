#%%
import os
import subprocess
import numpy as np
import pandas as pd
from datetime import datetime

from utilities import (
    find_nearest_matches,
    plot_2d_mapping,
    plot_3d_mapping
)

current_time = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))

#%%
## Specify parameters for file generation ##
############################################

openscad_path = "/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD" #Update this path as needed

eib_file = 'Neuralynx_EIB16-QC-H'
regions_file = 'CTX_TH_HPC_Bilateral_16Ch'
implant_name = '{e}_{r}'.format(e=eib_file, r=regions_file)
save_path = './GeneratedFiles/{i}_{t}'.format(i=implant_name, t=current_time)
if not os.path.exists(save_path):
    os.makedirs(save_path)

implant_height = 4.75 # this will be the height of the implant
ap_offset = 2 # this will be the AP offset from bregma; more positive from 0 is posterior

hole_radius = 0.22
implant_stl_file = os.path.abspath("./SCAD_Files/BlankMouseImplantShapedv4.stl")
depth_stl_file = os.path.abspath("./SCAD_Files/BlankDepthGuideShapedv4.stl")

depth_outer_radius = 0.6
depth_inner_radius = hole_radius + 0.05

# load boundary of the implant
implant_boundary = np.array(pd.read_csv('./EIB_Boundaries/{}.csv'.format(eib_file), header=None))
implant_boundary[:,1] -= ap_offset

sort_table_by = 'Region' # one of 'Region', 'Channel', or None

#%%
## Load EIB coordinates ##
##########################

eib_path = './EIBs/{}.csv'.format(eib_file)
eib_coords = pd.read_csv(eib_path)
eib_categories = eib_coords['Channel'].values

eib_coords['DV'] = implant_height

# separate ground and signal channels on EIB
eib_grounds = [('gnd' in region.lower()) | ('ground' in region.lower()) \
               for region in eib_coords['Channel']]
gnd_eib_coords = eib_coords[eib_grounds]
eib_coords = eib_coords[np.invert(eib_grounds)]

#%%
## Load brain region coordinates ##
###################################

# brain region coordinates are specified as (ML, AP, DV)
regions_path = './StereotaxCoords/{}.csv'.format(regions_file)
region_coords = pd.read_csv(regions_path)
region_categories = region_coords['Region'].values

# separate ground and signal brain region coordinates
gnd_regions = [('gnd' in region.lower()) | ('ground' in region.lower()) \
               for region in region_coords['Region']]
gnd_region_coords = region_coords[gnd_regions]
region_coords = region_coords[np.invert(gnd_regions)]

region_coords['AP'] += ap_offset # add AP offset from bregma
gnd_region_coords['AP'] += ap_offset

#%%
## Define nearest neighbors between EIB channels and brain regions ##
#####################################################################

signal_matches_df = find_nearest_matches(
    eib=eib_coords.copy(),
    regions=region_coords.copy()
)

gnd_matches_df = find_nearest_matches(
    eib=gnd_eib_coords.copy(),
    regions=gnd_region_coords.copy()
)

# combined df for both signal and ground
holes_df = pd.concat([
    signal_matches_df,
    gnd_matches_df
])
holes_df['Channel'] = pd.Categorical(holes_df['Channel'], categories=eib_categories)
holes_df['Region'] = pd.Categorical(holes_df['Region'], categories=region_categories)

hole_labels = holes_df['Channel']
hole_positions = holes_df[['rML','rAP','rDV']].values

#%%
## Make SCAD code for implant ##
################################

scad_code = f"// Import your STL model\nimport(\"{implant_stl_file}\");\n\n"

for _, row in holes_df.iterrows():
    label = row['Channel']
    entry = list(row[['eML','eAP','eDV']].values)
    exit  = list(row[['rML','rAP','rDV']].values)
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

implant_path = os.path.abspath(os.path.join(save_path, 'implant'))
with open(implant_path+'.scad', "w") as f:
    f.write(final_scad)

result = subprocess.run([
    openscad_path,
    "-o", implant_path+'.stl',
    implant_path+'.scad'
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error running OpenSCAD:")
    print(result.stderr)
else:
    print("✅ Implant.stl generated successfully!")

#%%
## Make SCAD code for depth guide ##
####################################

depth_guide_scad = f'import("{depth_stl_file}");\n\n'
depth_guide_scad1 = ''
depth_guide_scad2 = ''
for _, row in holes_df.iterrows():
    label = row['Channel']
    entry = list(row[['eML','eAP','eDV']].values)
    exit  = list(row[['rML','rAP','rDV']].values)
    if label.upper().startswith("GND"):
        r = depth_outer_radius + 0.1
    else:
        r = depth_outer_radius  
    height_depth = -exit[2]
    depth_guide_scad1 += f"""
    translate([{exit[0]}, {exit[1]}, {exit[2]:.4f}])
        cylinder(h = {height_depth:.4f}, r = {r}, $fn=60);
"""

for _, row in holes_df.iterrows():
    label = row['Channel']
    entry = list(row[['eML','eAP','eDV']].values)
    exit  = list(row[['rML','rAP','rDV']].values)
    if label.upper().startswith("GND"):
        r = depth_inner_radius + 0.1
    else:
        r = depth_inner_radius
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

depth_guide_path = os.path.abspath(os.path.join(save_path, 'depth_guide'))
# Write .scad file for wire depth guide
with open(depth_guide_path+'.scad', "w") as f:
    f.write(final_depth_guide_scad)

# Render STL for wire depth guide
result2 = subprocess.run([
    openscad_path,
    "-o", depth_guide_path+'.stl',
    depth_guide_path+'.scad'
], capture_output=True, text=True)

if result2.returncode != 0:
    print("❌ Error running OpenSCAD on DepthGuide:")
    print(result2.stderr)
else:
    print("✅ DepthGuide.stl generated successfully!")

#%%
## Generate and save channel mapping and plots ##
#############################

# save df of channel mapping
if sort_table_by is not None:
    holes_df = holes_df.sort_values(sort_table_by)

# round to prevent tiny trailing decimal values
holes_df.loc[:,['eML','eAP','eDV','rML','rAP','rDV']] = holes_df.loc[:,['eML','eAP','eDV','rML','rAP','rDV']].round(3)

holes_df.to_csv(os.path.abspath(os.path.join(save_path, 'channel_map.csv')))

# plot 2d mapping
df_2d = holes_df.copy()
df_2d['rAP'] -= ap_offset # reset ap_offset for plotting
df_2d['eAP'] -= ap_offset # reset ap_offset for plotting

if sort_table_by is not None:
    df_2d = df_2d.sort_values(sort_table_by)

plot_2d_mapping(
    df_2d,
    title=implant_name,
    save_path=save_path,
    current_time=current_time
    )

# plot 3d mapping
df_3d = holes_df.copy()
df_3d['rAP'] -= ap_offset # reset ap_offset for plotting
df_3d['eAP'] -= ap_offset # reset ap_offset for plotting
plot_3d_mapping(
    df_3d,
    implant_boundary=implant_boundary,
    implant_height=implant_height,
    title=implant_name,
    save_path=save_path,
    current_time=current_time
    )

print('{i} {t} Generation Complete.'.format(i=implant_name, t=current_time))