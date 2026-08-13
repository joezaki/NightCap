#%%
import os
import sys
import subprocess
import numpy as np
from stl import mesh
import pandas as pd
from datetime import datetime

import plotly.graph_objects as go
import dask
from tqdm import tqdm
from dask.distributed import Client, LocalCluster

from utilities import (
    scad_tunnel,
    plot_2d_implant,
    plot_3d_implant,
    get_updated_frame
)

current_time = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
save_path = f'../GeneratedFiles/Implant/{current_time}'
if not os.path.exists(save_path):
    os.makedirs(save_path)

#%%
############################################
## Specify parameters for file generation ##
############################################

regions_file = 'CTX_TH_HPC_Bilateral_16Ch' # file name where stereotaxic coords are stored

hole_radius = 0.23 # radius of each hole in implant
implant_height = 4.75 # in mm, one of [3, 4, 4.75]

depth_outer_radius = 0.55 # outer radius of each hole in depth guide
depth_inner_radius = hole_radius + 0.05

generate_rotating_gif = False # whether or not to save a gif of the rotating 3d implant
if generate_rotating_gif:
    cluster = LocalCluster(
        n_workers=16,
        threads_per_worker=1,
        memory_limit='8GB',
        dashboard_address=':8787',
        local_directory='./dask-worker-space'
        )
    client = Client(cluster)

#%%
###################################################################################
## Load brain region coordinates and empty STL files for implant and depth guide ##
###################################################################################

# find OpenSCAD path; update as needed
if sys.platform == 'win32':
    openscad_path = "C:/Program Files/OpenSCAD/openscad.exe"
elif sys.platform == 'darwin':
    openscad_path = "/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD"
else: # linux
    openscad_path = 'usr/bin/openscad'

# brain region coordinates are specified as (ML, AP, DV)
regions_df = pd.read_csv('../StereotaxCoords/{}.csv'.format(regions_file))

implant_stl = f'ImplantBlank_H{implant_height}mm'.replace('.', '_')
implant_stl_file = os.path.abspath(f"./SCAD_Files/{implant_stl}.stl").replace("\\", "/")
depth_stl_file = os.path.abspath("./SCAD_Files/DepthGuideBlank.stl").replace("\\", "/")

# #%%
# ################################
# ## Make SCAD code for implant ##
# ################################

# print("Generating implant.")
# scad_code = f"// Import your STL model\nimport(\"{implant_stl_file}\");\n\n"
# for _, row in regions_df.iterrows():
#     if row['Type'] != 'EMG':
#         coord = list(row[['ML','AP','DV']].values)
#         adjusted_coord = [coord[0], coord[1], 0] # for full hole
#         scad_code += scad_tunnel(
#             implant_height,
#             adjusted_coord,
#             hole_radius
#         )
# final_scad = f"""
# difference() {{
# {scad_code}
# }}
# """

# implant_path = os.path.abspath(os.path.join(save_path, 'implant'))
# with open(implant_path+'.scad', "w") as f:
#     f.write(final_scad)

# result = subprocess.run([
#     openscad_path,
#     "-o", implant_path+'.stl',
#     implant_path+'.scad'
# ], capture_output=True, text=True)

# if result.returncode != 0:
#     print("❌ Error running OpenSCAD:")
#     print(result.stderr)
# else:
#     print("✅ implant.stl generated successfully!")

# #%%
# ####################################
# ## Make SCAD code for depth guide ##
# ####################################

# print("Generating depth guide.")
# depth_guide_scad = f'import("{depth_stl_file}");\n\n'
# depth_guide_scad1 = ''
# depth_guide_scad2 = ''
# for _, row in regions_df.iterrows():
#     if row['Type'] != 'EMG':
#         coord  = list(row[['ML','AP','DV']].values)
#         height_depth = -coord[2]
#         depth_guide_scad1 += f"""
#         translate([{coord[0]}, {coord[1]}, {coord[2]:.4f}])
#             cylinder(h = {height_depth:.4f}, r = {depth_outer_radius}, $fn=60);
#     """

# for _, row in regions_df.iterrows():
#     if row['Type'] != 'EMG':
#         coord  = list(row[['ML','AP','DV']].values)
#         height_depth = -coord[2]
#         depth_guide_scad2 += f"""
#         translate([{coord[0]}, {coord[1]}, {coord[2]:.4f}])
#             cylinder(h = {height_depth:.4f}, r = {depth_inner_radius}, $fn=60);
#     """

# # Final SCAD: difference of outer – inner
# final_depth_guide_scad = f"""
# difference() {{
#     union() {{
# {depth_guide_scad}
# {depth_guide_scad1}
#     }}
# {depth_guide_scad2}
# }}

# """

# depth_guide_path = os.path.abspath(os.path.join(save_path, 'depth_guide'))
# # Write SCAD file for wire depth guide
# with open(depth_guide_path+'.scad', "w") as f:
#     f.write(final_depth_guide_scad)

# # Render STL for wire depth guide
# result2 = subprocess.run([
#     openscad_path,
#     "-o", depth_guide_path+'.stl',
#     depth_guide_path+'.scad'
# ], capture_output=True, text=True)

# if result2.returncode != 0:
#     print("❌ Error running OpenSCAD on DepthGuide:")
#     print(result2.stderr)
# else:
#     print("✅ depth_guide.stl generated successfully!")

#%%
#################################################
## Generate and save channel mapping and plots ##
#################################################

print('Saving regions.csv and visualizations.')
# round to prevent tiny trailing decimal values
regions_df.loc[:,['ML','AP','DV']] = regions_df.loc[:,['ML','AP','DV']].round(3)
regions_df.to_csv(os.path.abspath(os.path.join(save_path, 'regions.csv')))

# plot 2d mapping
plot_2d_implant(
    regions_df,
    title=regions_file,
    save_path=save_path,
    current_time=current_time
    )

# plot 3d mapping
implant_mesh = mesh.Mesh.from_file(implant_stl_file)
raw_vectors = implant_mesh.vectors 
all_vertices = raw_vectors.reshape(-1, 3)
implant_mesh = np.unique(all_vertices, axis=0)
fig = plot_3d_implant(
    regions_df,
    implant_mesh=implant_mesh,
    implant_height=implant_height,
    title=regions_file,
    save_path=save_path,
    current_time=current_time,
    return_fig=True
    )

print(f'{regions_file} Generation Complete in folder {current_time}.')

#%%
#############################################
## Generate 3D rotating GIF of the implant ##
#############################################

if generate_rotating_gif:

    # specify a list of angles of the implant to include in the gif
    angles = range(-180, 180, 3)

    delayed_frames = []
    cameras_ls = [{'center': {'x': 0, 'y': 0, 'z': 0},
                'eye': {'x': 2.5 * np.cos(np.radians(angle)),
                        'y': 2.5 * np.sin(np.radians(angle)),
                        'z': 1}} for angle in tqdm(angles)]
    delayed_frames = [dask.delayed(get_updated_frame)(fig, camera) for camera in cameras_ls]

    # compute; THIS LINE TAKES ~4min for 360 frames
    frames = dask.compute(*delayed_frames)

    # save the list of images as a GIF; this takes another ~1.5min for 360 frames
    if frames:
        frames[0].save(
            os.path.join(save_path, '3d_implant_animation.gif'),
            save_all=True,
            append_images=frames[1:],
            duration=100, # ms per frame
            loop=0
        )
        print("GIF saved successfully.")