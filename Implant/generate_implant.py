#%%
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from datetime import datetime

import plotly.graph_objects as go
from tqdm import tqdm
from dask.distributed import Client, LocalCluster

from utilities import (
    scad_tunnel,
    plot_implant_depth_guide,
    plot_2d_implant,
    plot_3d_implant,
    figs_to_gif
)

if __name__ == '__main__':

    current_time = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
    save_path = f'../GeneratedFiles/Implant/{current_time}'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    #%%
    ########################
    ## Specify parameters ##
    ########################

    brain_regions_csv = 'CTX_TH_HPC_Bilateral_16Ch' # file name where stereotaxic coords are stored

    hole_radius = 0.23 # radius of each hole in implant
    implant_height = 4.75 # in mm, one of [3, 4, 4.75]

    depth_outer_radius = 0.55 # outer radius of each hole in depth guide
    depth_inner_radius = hole_radius + 0.05

    generate_rotating_gif = True # whether or not to save a gif of the rotating 3d implant
    rotating_gif_step_size = 10 # step size in degrees for each frame in rotating gif

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
    regions_file = brain_regions_csv.split('.')[0]
    regions_df = pd.read_csv('../StereotaxCoords/{}.csv'.format(regions_file))

    implant_stl = f'ImplantBlank_H{implant_height}mm'.replace('.', '_')
    implant_stl_file = os.path.abspath(f"./SCAD_Files/{implant_stl}.stl").replace("\\", "/")
    depth_stl_file = os.path.abspath("./SCAD_Files/DepthGuideBlank.stl").replace("\\", "/")

    #%%
    ################################
    ## Make SCAD code for implant ##
    ################################

    print("generating implant.")
    scad_code = f"// Import your STL model\nimport(\"{implant_stl_file}\");\n\n"
    for _, row in regions_df.iterrows():
        if row['Type'] != 'EMG':
            coord = list(row[['ML','AP','DV']].values)
            adjusted_coord = [coord[0], coord[1], 0] # for full hole
            scad_code += scad_tunnel(
                implant_height,
                adjusted_coord,
                hole_radius
            )
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
        print("❌ error running OpenSCAD:")
        print(result.stderr)
    else:
        print("✅ implant.stl generated successfully!")

    #%%
    ####################################
    ## Make SCAD code for depth guide ##
    ####################################

    print("generating depth guide.")
    depth_guide_scad = f'import("{depth_stl_file}");\n\n'
    depth_guide_scad1 = ''
    depth_guide_scad2 = ''
    for _, row in regions_df.iterrows():
        if row['Type'] != 'EMG':
            coord  = list(row[['ML','AP','DV']].values)
            height_depth = -coord[2]
            depth_guide_scad1 += f"""
            translate([{coord[0]}, {coord[1]}, {coord[2]:.4f}])
                cylinder(h = {height_depth:.4f}, r = {depth_outer_radius}, $fn=60);
        """

    for _, row in regions_df.iterrows():
        if row['Type'] != 'EMG':
            coord  = list(row[['ML','AP','DV']].values)
            height_depth = -coord[2]
            depth_guide_scad2 += f"""
            translate([{coord[0]}, {coord[1]}, {coord[2]:.4f}])
                cylinder(h = {height_depth:.4f}, r = {depth_inner_radius}, $fn=60);
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
    # Write SCAD file for wire depth guide
    with open(depth_guide_path+'.scad', "w") as f:
        f.write(final_depth_guide_scad)

    # Render STL for wire depth guide
    result2 = subprocess.run([
        openscad_path,
        "-o", depth_guide_path+'.stl',
        depth_guide_path+'.scad'
    ], capture_output=True, text=True)

    if result2.returncode != 0:
        print("❌ error running OpenSCAD:")
        print(result2.stderr)
    else:
        print("✅ depth_guide.stl generated successfully!")

    #%%
    #################################################
    ## Generate and save channel mapping and plots ##
    #################################################

    print('saving regions.csv and visualizations.')
    # round to prevent tiny trailing decimal values
    regions_df.loc[:,['ML','AP','DV']] = regions_df.loc[:,['ML','AP','DV']].round(3)
    regions_df.to_csv(os.path.abspath(os.path.join(save_path, 'regions.csv')))

    # plot implant and depth guide
    plot_implant_depth_guide(
        implant_path=implant_path+'.stl',
        depth_guide_path=depth_guide_path+'.stl',
        title=regions_file,
        save_path=save_path
    )

    # plot 2d mapping
    plot_2d_implant(
        regions_df,
        title=regions_file,
        save_path=save_path
        )

    # plot 3d mapping
    fig = plot_3d_implant(
        regions_df,
        implant_path=implant_path+'.stl',
        implant_height=implant_height,
        title=regions_file,
        save_path=save_path,
        return_fig=True
        )

    #%%
    #############################################
    ## Generate 3D rotating GIF of the implant ##
    #############################################

    if generate_rotating_gif:

        cluster = LocalCluster(
            n_workers=8,
            threads_per_worker=1,
            memory_limit='8GB',
            dashboard_address=':8787',
            local_directory='./dask-worker-space'
            )
        client = Client(cluster)

        # specify a list of angles of the implant to include in the gif
        angles = range(-180, 180, rotating_gif_step_size)

        frames = []
        for i, angle in enumerate(tqdm(angles)):
            camera = {
                'center': {'x': 0, 'y': 0, 'z': 0},
                'eye': {'x': 3 * np.cos(np.radians(angle)),
                        'y': 3 * np.sin(np.radians(angle)),
                        'z': 1.25}
                        }
            next_fig = go.Figure(fig.to_dict())
            next_fig.update_layout(scene_camera=camera)
            frames.append(next_fig)

        figs_to_gif(
            frames,
            save_path = os.path.join(save_path, '3d_implant_animation.gif'),
            temp_save_path=os.path.join(save_path, 'temp_gif_frames'),
            scale=2,
            duration=50,
            width=800,
            height=800,
            loop=0
            )
        print("GIF saved successfully.")

        client.close()

    print(f'{regions_file} generation complete in folder {current_time}.')