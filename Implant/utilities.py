import os
import math
import numpy as np
import pandas as pd
import shutil

import io
from PIL import Image
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def scad_tunnel(
        implant_height,
        coord,
        radius,
        extension=2,
        bottom_z=0.0
        ):
    """
    Creates a single vertical cylindrical hole centered on the
    stereotax coordinate.

    Parameters
    ----------
    implant_height : float
        height of the implant
    coord : [ML, AP, DV]
        stereotax coordinate
    radius : float
        hole radius
    extension : float
        extends the hole above the implant surface
    bottom_z : float
        bottom of the hole (typically 0 = bottom of implant)
    """

    top_z = implant_height + extension
    height = top_z - bottom_z

    return f"""
translate([{coord[0]:.4f},
           {coord[1]:.4f},
           {bottom_z:.4f}])
cylinder(
    h={height:.4f},
    r={radius:.4f},
    $fn=60
);
"""


def plot_2d_implant(
    regions_df,
    marker_size=18,
    title=None,
    save_path=None,
    return_fig=False
):
    '''
    Plots two subplots, a 2d mapping between eib channels and associated
    brain regions on the left, and a table with the mappings and brain region
    coordinates on the right.

    Note: All units are in mm.

    Parameters
    ==========
    regions_df : pandas df
        df representing the brain region stereotaxic coordinates
    marker_size : int
        size of the datapoints representing the eib channels and the brain region coordinates. default is 18.
    title : str
        optional title for the entire plot. default is None.
    save_path : str
        path to the directory where the plot will be saved. Default is None.
    return_fig : bool
        whether or not to return the fig object. Default is False.
    '''

    df = regions_df.copy()

    fig = make_subplots(cols=2, specs = [[{"type": "xy"}, {"type": "table"}]])

    # plot brain regions
    fig.add_trace(go.Scattergl(x=df['ML'], y=df['AP'], mode='markers+text', text=df['Region'],
                               textposition='top center', name='Brain',
                               hovertext=['ML:{ml}<br>AP:{ap}<br>DV:{dv}<br>{r}'.format(
                                   ml=np.round(row['ML'],3),
                                   ap=np.round(row['AP'],3),
                                   dv=np.round(row['DV'],3),
                                   r=row['Region']) for _,row in df.iterrows()],
                               marker=dict(color='teal', size=marker_size, line=dict(color='black', width=1))), row=1, col=1)

    # plot table with mapping and brain region coordinates
    table_cols = ['Region','ML','AP','DV','Type']
    df[['ML','AP','DV']] = df[['ML','AP','DV']].round(3)
    table_formats = np.repeat('str', len(table_cols))
    fig.add_trace(go.Table(header=dict(values=table_cols, fill_color='darkgrey', height=30),
                        cells=dict(values=df[table_cols].T.values.tolist(), height=30,
                        format=table_formats)), row=1, col=2)

    # configure plot
    fig.update_layout(template='simple_white', width=1600, height=800, showlegend=False,
                    xaxis_title='ML', yaxis_title='AP', font=dict(size=15),
                    title_text=title)
    fig.update_yaxes(title_font=dict(size=18), tickfont=dict(size=18), row=1, col=1)
    fig.update_xaxes(title_font=dict(size=18), tickfont=dict(size=18), row=1, col=1)
    config = {'toImageButtonOptions': {'format': 'svg'}}

    # optionally save
    if save_path is not None:
        save_path = os.path.abspath(save_path)
        output_file = os.path.join(save_path, f"2d_implant.html")
        if not os.path.exists(save_path):
            print('Making directory at: {}'.format(save_path))
            os.makedirs(save_path)
        fig.write_html(output_file, config=config)
    else:
        fig.show(config=config)

    if return_fig:
        return fig


def plot_3d_implant(
    regions_df,
    implant_mesh,
    implant_height,
    title=None,
    save_path=None,
    return_fig=False
):
    '''
    Plots a 3d rendering mapping channels on an EIB to its matched
    regions on an implant, through which wires should be connected.

    Note: All units are in millimeters.

    Parameters
    ==========
    regions_df : pandas df
        df representing the brain region stereotaxic coordinates
    implant_mesh : numpy array
        a numpy array representing the vertices of the implant, for drawing the mesh
    implant_height : float
        the height of the implant in millimeters, for drawing.
    title : str
        optional title for the entire plot. default is None.
    save_path : str
        path to the directory where the plot will be saved. Default is None.
    return_fig : bool
        whether or not to return the fig object. Default is False.
    '''

    df = regions_df.copy()
    fig = go.Figure()

    # plot mesh for implant outline
    fig.add_trace(go.Mesh3d(x=implant_mesh[:,0], y=implant_mesh[:,1], z=implant_mesh[:,2],
                            color='lightgrey', opacity=0.5, alphahull=0.1, name='Implant',
                            hoverinfo='none', showlegend=True))

    # plot holes for implant
    fig.add_trace(go.Scatter3d(x=df['ML'], y=df['AP'], z=np.repeat(implant_height, df.shape[0]),
                               text=df['Region'], mode='markers', marker=dict(color='teal', size=10),
                               hoverinfo='text', showlegend=True, name='Regions',
                               hovertext=['Region {r}<br>ML: {ml}<br>AP: {ap}<br>DV: {dv}'.format(
                                   r=row['Region'],
                                   ml=np.round(row['ML'],3),
                                   ap=np.round(row['AP'],3),
                                   dv=np.round(row['DV'],3)) for _,row in df.iterrows()]))

    # plot depth of each wire for each brain region
    for i, region in df.iterrows():
        showlegend= True if i == 0 else False
        fig.add_trace(go.Scatter3d(x=np.repeat(region['ML'],2), y=np.repeat(region['AP'],2), z=[implant_height,region['DV']],
                                   mode='lines', line=dict(color='purple', width=4), name='Electrode Wires',
                                   hovertext='Region: {r}<br>ML: {ml}<br>AP: {ap}<br>DV: {dv}'.format(
                                       r=region['Region'],
                                       ml=np.round(region['ML'],3),
                                       ap=np.round(region['AP'],3),
                                       dv=np.round(region['DV'],3)),
                                       hoverinfo='text',
                                       showlegend=showlegend,
                                       legendgroup='wires'))

    # configure plot
    fig.update_layout(template='simple_white', width=800, height=800, font=dict(size=15), showlegend=True,
                      title_text=title, margin=dict(t=80, r=0, l=0, b=0),
                      scene=dict(xaxis_title='ML', yaxis_title='AP', zaxis_title='DV'),
                      scene_camera=dict(center=dict(z=-.15), eye=dict(x=-.8, y=-2, z=0.7)))
    config = {'toImageButtonOptions': {'format': 'svg'}}

    # optionally save
    if save_path is not None:
        save_path = os.path.abspath(save_path)
        output_file = os.path.join(save_path, f"3d_implant.html")
        if not os.path.exists(save_path):
            print('Making directory at: {}'.format(save_path))
            os.makedirs(save_path)
        fig.write_html(output_file, config=config)
    else:
        fig.show(config=config)

    if return_fig:
        return fig

def figs_to_gif(
        figs,
        save_path,
        temp_save_path='./temp_gif_frames',
        format='png',
        scale=2,
        height=800,
        width=800,
        duration=100,
        loop=0
        ):
    '''
    For a given list of frame images, create and save a gif looping through them.

    Parameters
    ==========
    figs : list
        list of plotly figures to stitch together.
    save_path : str
        directory including file name and extension to which to save final gif.
    temp_save_path : str
        directory where frames will temporarily be stored. Default is './temp_gif_frames'.
    format : str
        format to save frames in. One of ['png', 'jpg', 'jpeg', 'webp', 'svg', 'pdf']. Default is 'png'.
    scale : int or float
        scaling factor to up- or down-scale saved images. Default is 2.
    height, width : int
        height and width that each frame will be saved at, respectively. Defaults are 800.
    duration : int
        duration of each frame in ms. Default is 100.
    loop : int
        number of times to loop through the frames, infinite if 0. Default is 0.
    '''

    # make temporary save path for frames, create filenames
    temp_save_path = os.path.abspath(temp_save_path)
    if not os.path.exists(temp_save_path):
        os.makedirs(temp_save_path)
    filenames = [os.path.join(temp_save_path, f'frame{i}.{format}') \
                 for i in range(len(figs))]
    
    # temporarily save frames (most time intensive step)
    print('saving temporary frame files.')
    print(f'keep track of progress in {temp_save_path}')
    plotly.io.write_images(
        fig=figs,
        file=filenames,
        scale=scale,
        height=height,
        width=width
        )
    print('temporary frame files saved.')

    # load saved frames
    frames = [Image.open(file) for file in filenames]

    # write gif
    if frames:
        frames[0].save(
            save_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration, # ms per frame
            loop=loop
        )
        print("GIF saved successfully.")
    
    # delete saved frames
    shutil.rmtree(temp_save_path)
    print('temporary frame files deleted.')