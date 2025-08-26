import os
import math
import numpy as np
import pandas as pd
import cvxpy as cp

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def find_nearest_matches(
        eib,
        regions,
        verbose=False):
    '''
    Find nearest match between all EIB channels and brain regions.
    Note that there len(eib) >= len(regions) or else this will error.

    Parameters
    ==========
    eib : pandas df
        a pandas df representing the eib channels and their associated 'ML', 'AP', and 'DV' coordinates.
    regions : pandas df
        a pandas df representing the brain regions and their associated 'ML', 'AP', and 'DV' coordinates.
    verbose : boolean
        whether or not to print the matches
    '''

    assert len(eib) >= len(regions), 'There must be at least as many EIB channels as there are brain regions.'
    len_eib, len_regions = eib.shape[0], regions.shape[0]

    # create cost matrix
    # C[i, j] is the squared Euclidean distance between point A_i and point B_j
    cost_matrix = cp.pnorm(cp.reshape(eib[['ML','AP']], (len_eib, 1, 2), 'C') - cp.reshape(regions[['ML','AP']], (1, len_regions, 2), 'C'), p=2, axis=2)**2
    cost_matrix_val = cost_matrix.value  # Precompute the cost matrix

    # define the CVXPY problem variables
    P = cp.Variable((len_eib, len_regions), nonneg=True)

    # define the objective function
    objective = cp.Minimize(cp.sum(cp.multiply(cost_matrix_val, P)))

    # define the constraints
    # Each point in EIB may not be matched
    row_constraints = [cp.sum(P, axis=1) <= 1]
    # Each point in brain regions must be matched
    col_constraints = [cp.sum(P, axis=0) == 1]
    constraints = row_constraints + col_constraints

    # solve
    problem = cp.Problem(objective, constraints)
    problem.solve()
    matches = np.where(np.round(P.value) == 1)

    if verbose:
        print("\nMatches (A_i -> B_j):")
        for i, j in zip(matches[0], matches[1]):
            print(f"Point A_{i} matched to Point B_{j}")

    # the coords prefix 'e' is for EIB and 'r' for Region (i.e., brain region)
    matches_df = pd.DataFrame({'Channel':eib.iloc[matches[0]]['Channel'].values,
                               'Region' :regions.iloc[matches[1]]['Region'].values,
                               'eML':    eib.iloc[matches[0]]['ML'].values,
                               'eAP':    eib.iloc[matches[0]]['AP'].values,
                               'eDV':    eib.iloc[matches[0]]['DV'].values,
                               'rML':regions.iloc[matches[1]]['ML'].values,
                               'rAP':regions.iloc[matches[1]]['AP'].values,
                               'rDV':regions.iloc[matches[1]]['DV'].values}
                               ).reset_index(drop=True)
    
    return matches_df


def plot_2d_mapping(
    holes_df,
    marker_size=18,
    title=None,
    save_path=None,
    current_time=None
):
    '''
    Plots two subplots, a 2d mapping between eib channels and associated
    brain regions on the left, and a table with the mappings and brain region
    coordinates on the right.

    Note: All units are in mm.

    Parameters
    ==========
    holes_df : pandas df
        df representing the matched eib channels and brain regions, with their associated coordinates
    marker_size : int
        size of the datapoints representing the eib channels and the brain region coordinates. default is 18.
    title : str
        optional title for the entire plot. default is None.
    save_path : str
        path to the directory where the plot will be saved. Default is None.
    current_time : str
        a datetime-based string to attach to the file name when created.
    '''

    df = holes_df.copy()

    fig = make_subplots(cols=2, specs = [[{"type": "xy"}, {"type": "table"}]])

    # plot eib channels
    fig.add_trace(go.Scattergl(x=df['eML'], y=df['eAP'], mode='markers+text', text=df['Channel'],
                               textposition='top center', hovertext=df['Region'], name='EIB',
                               marker=dict(color='gold', size=marker_size, line=dict(color='black', width=1))), row=1, col=1)

    # plot brain regions
    fig.add_trace(go.Scattergl(x=df['rML'], y=df['rAP'], mode='markers+text', text=df['Region'],
                               textposition='top center', hovertext=df['Channel'], name='Brain',
                               marker=dict(color='white', size=marker_size, line=dict(color='black', width=1))), row=1, col=1)

    # plot mapping between EIB channels and brain regions
    for _, match in df.iterrows():
        fig.add_trace(go.Scattergl(x=match[['eML','rML']], y=match[['eAP','rAP']],
                                mode='lines', line=dict(color='slategrey', width=2)), row=1, col=1)

    # plot table with mapping and brain region coordinates
    df.rename(columns={'rML':'ML','rAP':'AP', 'rDV':'DV'}, inplace=True)
    table_cols = ['Channel','Region','ML','AP','DV']
    df[['ML','AP','DV']] = df[['ML','AP','DV']].round(3)
    table_formats = np.repeat('str', len(table_cols))
    fig.add_trace(go.Table(header=dict(values=table_cols, fill_color='darkgrey', height=30),
                        cells=dict(values=df[table_cols].T.values.tolist(), height=30,
                        format=table_formats)), row=1, col=2)

    # configure plot
    fig.update_layout(template='simple_white', width=1600, height=800, showlegend=False,
                    xaxis_title='ML', yaxis_title='AP', font=dict(size=15),
                    title_text=title)

    # optionally save
    if save_path is not None:
        save_path = os.path.abspath(save_path)
        output_file = os.path.join(save_path, "2d_implant_mapping_{t}.html".format(t=current_time))
        if not os.path.exists(save_path):
            print('Making directory at: {}'.format(save_path))
            os.makedirs(save_path)
        fig.write_html(output_file)
    else:
        fig.show()


def plot_3d_mapping(
    holes_df,
    implant_boundary,
    implant_height,
    eib_offset=2,
    title=None,
    save_path=None,
    current_time=None
):
    '''
    Plots a 3d rendering mapping channels on an EIB to its matched
    regions on an implant, through which wires should be connected.

    Note: All units are in millimeters.

    Parameters
    ==========
    holes_df : pandas df
        df representing the matched eib channels and brain regions, with their associated coordinates
    implant_boundary : numpy array
        a 2d numpy array representing the vertices of the implant, for drawing the mesh
    implant_height : float
        the height of the implant in millimeters, for drawing.
    eib_offset : int or float
        the vertical distance between the surface of the implant and the eib. default is 2.
    title : str
        optional title for the entire plot. default is None.
    save_path : str
        path to the directory where the plot will be saved. Default is None.
    current_time : str
        a datetime-based string to attach to the file name when created.
    '''

    # construct mesh coordinates for implant
    implant_mesh = np.concatenate((implant_boundary, 
                                np.repeat(implant_height, implant_boundary.shape[0]).reshape((implant_boundary.shape[0],1))), axis=1)
    implant_mesh = np.append(implant_mesh,
                            np.concatenate((implant_boundary, 
                                            np.repeat(0, implant_boundary.shape[0]).reshape((implant_boundary.shape[0],1))), axis=1), axis=0)

    fig = go.Figure()

    # plot mesh for implant outline
    fig.add_trace(go.Mesh3d(x=implant_mesh[:,0], y=implant_mesh[:,1], z=implant_mesh[:,2],
                            color='grey', opacity=0.5, alphahull=0.1, name='Implant'))

    # show mesh for eib (using the boundaries around the eib channels)
    fig.add_trace(go.Mesh3d(x=holes_df['eML'], y=holes_df['eAP'], z=holes_df['eDV']+eib_offset,
                            color='gold', opacity=0.5, name='EIB'))

    # plot holes for implant
    fig.add_trace(go.Scatter3d(x=holes_df['rML'], y=holes_df['rAP'], z=np.repeat(implant_height, holes_df.shape[0]),
                               text=holes_df['Region'], mode='markers', marker=dict(color='white', size=10)))

    # plot eib channels
    fig.add_trace(go.Scatter3d(x=holes_df['eML'], y=holes_df['eAP'], z=np.repeat(implant_height+eib_offset, holes_df.shape[0]),
                               text=holes_df['Channel'], mode='markers+text', marker=dict(color='gold', size=10)))

    # plot mapping between EIB channels and brain regions
    for _, match in holes_df.iterrows():
        fig.add_trace(go.Scatter3d(x=match[['eML','rML']], y=match[['eAP','rAP']], z=[implant_height+eib_offset,implant_height],
                                   mode='lines', line=dict(color='slategrey', width=5)))
        fig.add_trace(go.Scatter3d(x=np.repeat(match['rML'],2), y=np.repeat(match['rAP'],2), z=[implant_height,match['rDV']],
                                   mode='lines', line=dict(color='purple', width=4), name='{e}; {r}'.format(e=match['Channel'], r=match['Region'])))

    # configure plot
    fig.update_layout(template='simple_white', width=800, height=800, font=dict(size=15), showlegend=False,
                      title_text=title, margin=dict(t=80, r=0, l=0, b=0),
                      scene=dict(xaxis_title='ML', yaxis_title='AP', zaxis_title='DV'),
                      scene_camera=dict(center=dict(z=-.15), eye=dict(x=-.8, y=-2, z=0.7)))

    # optionally save
    if save_path is not None:
        save_path = os.path.abspath(save_path)
        output_file = os.path.join(save_path, "3d_implant_mapping{t}.html".format(t='_'+current_time))
        if not os.path.exists(save_path):
            print('Making directory at: {}'.format(save_path))
            os.makedirs(save_path)
        fig.write_html(output_file)
    else:
        fig.show()