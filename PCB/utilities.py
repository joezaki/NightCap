import sys
import os
import glob
import subprocess

import pcbnew
import csv
import math
from functools import partial
import shutil


def draw_csv_outline(
        csv_path,
        board,
        board_offset_x,
        board_offset_y,
        line_thickness=0.15
        ):
    """
    (For Top and Bottom PCBs)
    Read PCB outline points from a CSV.

    Parameters
    ==========
    csv_path : str
        path to csv file with vertices. Columns should be
        ['Point', 'X_mm', 'Y_mm', 'Type']
    board : pcbnew.BOARD
        Current board
    board_offset_x, board_offset_y : float
        distance in mm from origin of canvas where edge cuts will be drawn
    line_thickness : float
        thickness of edge cuts line. Default is 0.15.

    Type behavior
    =============
        Line     -> draw from previous point to current point
        Midpoint -> save point but draw nothing
        Arc      -> use previous two points and current point
        Blank    -> save point but draw nothing
    """

    edge_cuts = pcbnew.Edge_Cuts
    line_width = pcbnew.FromMM(line_thickness)

    previous_points = []
    with open(
            csv_path,
            mode="r",
            newline="",
            encoding="utf-8-sig"
            ) as csv_file:

        reader = csv.DictReader(csv_file, dialect=csv.excel)
        required_columns = ["X_mm", "Y_mm", "Type"]
        for column in required_columns:
            if column not in reader.fieldnames:
                raise ValueError(
                    f"CSV is missing column: "
                    f"{column}\n"
                    f"Found columns: "
                    f"{reader.fieldnames}"
                )

        for row_number, row in enumerate(reader, start=2):
            try:
                x = float(row["X_mm"])
                y = float(row["Y_mm"])
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid X or Y value "
                    f"on row {row_number}:\n"
                    f"{row}"
                )

            point_type = (row.get("Type", "") or "")
            point_type = (point_type.strip().lower())

            # convert to KiCad's coordinate system
            current_point = pcbnew.VECTOR2I_MM(
                x + board_offset_x,
                -y + board_offset_y
            )

            if point_type == "line":
                if len(previous_points) < 1:
                    raise ValueError(
                        f"Line on row {row_number} "
                        f"has no previous point.")
                line = pcbnew.PCB_SHAPE(board)
                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                line.SetLayer(edge_cuts)
                line.SetWidth(line_width)
                line.SetStart(previous_points[-1])
                line.SetEnd(current_point)
                board.Add(line)

            elif point_type == "arc":
                if len(previous_points) < 2:
                    raise ValueError(
                        f"Arc on row {row_number} "
                        f"needs two previous points."
                    )
                arc = pcbnew.PCB_SHAPE(board)
                arc.SetShape(pcbnew.SHAPE_T_ARC)
                arc.SetLayer(edge_cuts)
                arc.SetWidth(line_width)
                arc.SetArcGeometry(
                    previous_points[-2],
                    previous_points[-1],
                    current_point
                )
                board.Add(arc)

            elif point_type in ("", "midpoint"):
                # save the point but do not draw (for arc)
                pass

            else:
                raise ValueError(
                    f"Unknown Type on row "
                    f"{row_number}: "
                    f"'{point_type}'\n"
                    f"Use Line, Midpoint, Arc, "
                    f"or leave it blank."
                )

            previous_points.append(current_point)


def add_outer_holes(
    outer_holes_csv,
    board,
    board_offset_x,
    board_offset_y,
    pad_diameter_mm=1.3,   # standard 0.1" header pad OD
    drill_diameter_mm=0.9, # standard 0.1" header pin drill (0.9-1.0mm typical)
):
    '''
    (For Top and Bottom PCBs)
    Given a path to a CSV file of outer pad coordinates, add a through-hole
    (PTH) pad sized for header pins for each coordinate to the board.
    '''
    outer_pads = []
    with open(outer_holes_csv, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # columns are Ch, X, Y
        for row in reader:
            ch, x, y = row[0], float(row[2]), float(row[1])
            x += board_offset_x
            y += board_offset_y

            footprint = pcbnew.FOOTPRINT(board)
            footprint.SetFPID(pcbnew.LIB_ID("Generated", "HeaderPad"))
            footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
            footprint.SetReference(f"Pad_{ch}")
            footprint.SetValue(ch)

            # add pad, configure as PTH, and translate
            pad = pcbnew.PAD(footprint)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetSize(pcbnew.VECTOR2I_MM(pad_diameter_mm, pad_diameter_mm))
            pad.SetDrillSize(pcbnew.VECTOR2I_MM(drill_diameter_mm, drill_diameter_mm))
            pad.SetPosition(pcbnew.VECTOR2I_MM(x, y))
            pad.SetLayerSet(pcbnew.PAD.PTHMask())
            pad.SetPadName(ch)
            footprint.Add(pad)

            # courtyard sized to actual pad radius
            courtyard_radius = pad_diameter_mm / 2 + 0.05
            courtyard = pcbnew.PCB_SHAPE(footprint)
            courtyard.SetShape(pcbnew.SHAPE_T_CIRCLE)
            courtyard.SetLayer(pcbnew.F_CrtYd)
            courtyard.SetWidth(pcbnew.FromMM(0.05))
            courtyard.SetCenter(pcbnew.VECTOR2I_MM(x, y))
            courtyard.SetStart(pcbnew.VECTOR2I_MM(x, y))
            courtyard.SetEnd(pcbnew.VECTOR2I_MM(x + courtyard_radius, y))
            footprint.Add(courtyard)

            outer_pads.append({'x': x, 'y': y, 'obj': pad, 'ch': ch})
            board.Add(footprint)

    return outer_pads


def add_inner_vias(
        brain_regions_csv,
        board,
        board_offset_x,
        board_offset_y
        ):
    '''
    (For Bottom PCB)
    Given a path to a CSV file of stereotaxic coordinates,
    add a via for each brain region to the board.
    '''

    inner_vias = []
    with open(brain_regions_csv, 'r') as f:
        reader = csv.reader(f)
        header = next(reader) # skip header

        for row in reader:
            ch, x, y = row[0], float(row[1]), -float(row[2])
            ap, ml, dv = row[2], row[1], row[3]
            x += board_offset_x
            y += board_offset_y

            # create footprint wrapper for the wire hole
            footprint = pcbnew.FOOTPRINT(board)
            footprint.SetFPID(pcbnew.LIB_ID("Generated", "WireHole"))
            footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
            footprint.SetReference(f"Via_{ch}")

            # create plated through-hole (PTH) pad
            pad = pcbnew.PAD(footprint)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)

            # size and position
            pad.SetSize(pcbnew.VECTOR2I_MM(0.45, 0.45))
            pad.SetDrillSize(pcbnew.VECTOR2I_MM(0.2, 0.2))
            pad.SetPosition(pcbnew.VECTOR2I_MM(x, y))
            pad.SetLayerSet(pad.PTHMask()) 
            pad.SetPadName(ch)
            footprint.Add(pad)
            board.Add(footprint)

            inner_vias.append({
                'x': x,
                'y': y,
                'obj': pad,
                'ch': ch,
                'ap':ap,
                'ml':ml,
                'dv':dv
                })
    return inner_vias


def get_angle(item, cy, cx):
    return math.atan2(item['y'] - cy, item['x'] - cx)


def match_vias_holes(
        outer_holes,
        inner_vias,
        board
):
    '''
    (For Bottom PCB)
    Given two lists of outer PTH and inner vias, match the GND & REF channels first,
    then match the remaining vias to their nearest radially positioned PTH.
    '''
    # look for GND and REF vias & through-holes
    gnd_via = next((v for v in inner_vias if v['ch'].upper() == 'GND'), None)
    gnd_hole = next((p for p in outer_holes if p['ch'].upper() == 'GND'), None)
    ref_via = next((v for v in inner_vias if v['ch'].upper() == 'REF'), None)
    ref_hole = next((p for p in outer_holes if p['ch'].upper() == 'REF'), None)

    # filter them out to get remaining pairs 
    rem_vias = [v for v in inner_vias if v['ch'].upper() not in ['GND', 'REF']]
    rem_holes = [p for p in outer_holes if p['ch'].upper() not in ['GND', 'REF']]

    pairs = []

    # match GND and REF (if they exist)
    if gnd_via and gnd_hole:
        pairs.append((gnd_via, gnd_hole, "GND"))
    if ref_via and ref_hole:
        pairs.append((ref_via, ref_hole, "REF"))

    # match remaining vias to the remaining through-holes radially using the center of mass
    cx = sum(v['x'] for v in rem_vias) / len(rem_vias)
    cy = sum(v['y'] for v in rem_vias) / len(rem_vias)

    rem_vias.sort(key=partial(get_angle, cx=cx, cy=cy))
    rem_holes.sort(key=partial(get_angle, cx=cx, cy=cy))

    for i in range(min(len(rem_vias), len(rem_holes))):
        via = rem_vias[i]
        hole = rem_holes[i]
        pairs.append((via, hole, hole['ch']))

    for via, hole, net_suffix in pairs:
        net_name = f"Net_{net_suffix}"
        
        # add Net match between via & through-hole
        new_net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(new_net)
        net_code = new_net.GetNetCode()
        via['obj'].SetNetCode(net_code)
        hole['obj'].SetNetCode(net_code)
        print(f"Inner via '{via['ch']}' mapped to outer PTH '{hole['ch']}' -> {net_name}")
    return cx, cy


def place_footprint(
        board,
        library_path,
        footprint_name,
        x_mm,
        y_mm,
        rotation_deg=0,
        reference="J1",
        value=None
        ):
    '''
    (For Top PCB)
    Place KiCad footprint for connector onto the top PCB.

    Parameters
    ==========
    board : pcbnew.BOARD
        Current board
    library_path : str
        Folder containing the .kicad_mod footprint
    footprint_name : str
        Name of the footprint (without .kicad_mod)
    x_mm, y_mm : float
        Position in mm
    rotation_deg : float
        Rotation in degrees
    reference : str
        Reference designator
    value : str
        Value text. Defaults to footprint name
    '''

    footprint = pcbnew.FootprintLoad(library_path, footprint_name)

    if footprint is None:
        raise RuntimeError(
            f"Could not load footprint '{footprint_name}' "
            f"from '{library_path}'."
        )

    footprint.SetReference(reference)

    if value is None:
        value = footprint_name
    footprint.SetValue(value)

    footprint.SetPosition(
        pcbnew.VECTOR2I(
            pcbnew.FromMM(x_mm),
            pcbnew.FromMM(y_mm)
        ))

    footprint.SetOrientationDegrees(rotation_deg)
    board.Add(footprint)

    return footprint


def get_pad_location_info(connector):
    '''
    (For Top PCB)
    Extract location and channel info for
    all pads from a connector footprint.
    '''

    pads = {}
    for pad in connector.Pads():

        pad_name = pad.GetNumber().strip()
        pos = pad.GetPosition()

        pads[pad_name] = {
            "ch": pad_name,
            "obj": pad,
            "x": pcbnew.ToMM(pos.x),
            "y": pcbnew.ToMM(pos.y)
        }

    return pads


def load_pin_to_hole_matching_csv(
        filename,
        holes,
        pins
        ):
    '''
    (For Top PCB)
    Loads matched channels between inner connector pins
    and outer through-holes on PCB.
    '''

    pairs = []
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        for row in rows:
            pin_name = row["Pin"].strip()
            hole_name = row["PTH"].strip()

            if pin_name not in pins:
                print(f"Missing pin {pin_name}")
                continue

            if hole_name not in holes:
                print(f"Missing connector pad {hole_name}")
                continue

            pairs.append((
                pins[pin_name],
                holes[hole_name],
                pin_name
                ))
    return pairs


def label_outer_holes(
        outer_holes,
        cx,
        cy,
        board
        ):
    '''
    (For Top and Bottom PCBs)
    Add channel number silkscreen labels to outer through-holes.
    '''
    f_silk = pcbnew.F_SilkS
    for pad_data in outer_holes:
        pad_obj = pad_data['obj']
        x, y = pad_data['x'], pad_data['y']
        ch_name = pad_obj.GetPadName()
        
        label = pcbnew.PCB_TEXT(board)
        label.SetText(ch_name)
        
        # nudge the label 1.0mm towards the center so it sits just inside the pad
        angle = math.atan2(cy - y, cx - x)
        lbl_x = x + (1.0 * math.cos(angle))
        lbl_y = y + (1.0 * math.sin(angle))
        
        label.SetPosition(pcbnew.VECTOR2I_MM(lbl_x, lbl_y))
        label.SetLayer(f_silk)
        label.SetTextSize(pcbnew.VECTOR2I_MM(0.3, 0.3))
        board.Add(label)


def label_inner_vias(
        brain_regions_csv,
        board_offset_x,
        board_offset_y,
        board
        ):
    '''
    (For Bottom PCB)
    Given a path to a CSV file of brain region stereotaxic coordinates,
    label each region's name on the bottom silkscreen.
    '''
    b_silk = pcbnew.B_SilkS
    
    with open(brain_regions_csv, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            region = row[0]
            # Calculate raw position identical to via placement
            raw_x = float(row[1]) + board_offset_x
            raw_y = -float(row[2]) + board_offset_y
            
            # Shift initial x position to left if on left hemisphere, right if right
            if region[-1] == 'L':
                x = raw_x - (0.25*len(region.split('_')[0]))
            else: # if R or anything else, move right
                x = raw_x + (0.25*len(region.split('_')[0]))
            y = raw_y
            
            via_label = pcbnew.PCB_TEXT(board)
            via_label.SetText(region.split('_')[0])
            via_label.SetPosition(pcbnew.VECTOR2I_MM(x, y))
            via_label.SetLayer(b_silk) # Placing on Bottom Silk
            via_label.SetTextSize(pcbnew.VECTOR2I_MM(0.3, 0.3))
            via_label.SetMirrored(True)
            via_label.SetTextThickness(pcbnew.FromMM(0.1))
            board.Add(via_label)


def draw_silk_line(start_mm, end_mm, layer, board):
    '''
    (For Bottom PCB)
    Draw line on bottom silkscreen (for bregma, lambda, and midline).
    '''
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetLayer(layer)
    line.SetWidth(pcbnew.FromMM(0.15))
    line.SetStart(pcbnew.VECTOR2I_MM(start_mm[0], start_mm[1]))
    line.SetEnd(pcbnew.VECTOR2I_MM(end_mm[0], end_mm[1]))
    board.Add(line)


def draw_magnet_circle(center_x, center_y, radius, board, b_silk):
    '''
    (For Top and Bottom PCBs)
    Draw circle on bottom silkscreen for where magnets will go (if using).
    '''
    circle = pcbnew.PCB_SHAPE(board)
    circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
    circle.SetLayer(b_silk)
    circle.SetWidth(pcbnew.FromMM(0.15))
    circle.SetCenter(pcbnew.VECTOR2I_MM(center_x, center_y))
    circle.SetStart(pcbnew.VECTOR2I_MM(center_x, center_y))
    circle.SetEnd(pcbnew.VECTOR2I_MM(center_x + radius, center_y))
    board.Add(circle)


def auto_route_board(save_path):
    '''
    (For Top and Bottom PCB)
    Locate the installed Freerouting JAR, export the current board to a Specctra DSN, 
    run the autorouter headlessly, import the finished SES file, and save it.
    '''
    # find the freerouting.jar installed by KiCad PCM
    if sys.platform == 'win32':
        base_path = os.path.expandvars(r"%USERPROFILE%\Documents\KiCad\*\3rdparty\plugins")
    elif sys.platform == 'darwin':
        base_path = os.path.expanduser("~/Documents/KiCad/*/3rdparty/plugins")
    else: # linux
        base_path = os.path.expanduser("~/.local/share/kicad/*/3rdparty/plugins")
        
    search_pattern = os.path.join(base_path, "**", "freerouting*.jar")
    matches = glob.glob(search_pattern, recursive=True)
    
    if not matches:
        print("Error: Could not find freerouting.jar. Ensure the plugin is installed.")
        return
        
    jar_path = matches[0]
    print(f"Found Freerouting JAR: {jar_path}")
    
    # define permanent paths for Specctra files in the project folder
    dsn_path = os.path.abspath(os.path.join(save_path, "autoroute.dsn"))
    ses_path = os.path.abspath(os.path.join(save_path, "autoroute.ses"))
    
    # export the current board state
    print(f"Exporting DSN to {dsn_path}.")
    pcbnew.ExportSpecctraDSN(dsn_path)
    
    # run freerouting
    print("Running Freerouting (KiCad may freeze while it routes).")
    cmd = [
        "java", "-jar", jar_path,
        "-de", dsn_path,
        "-do", ses_path,
        "-mp", "10" 
    ]
    
    try:
        subprocess.run(cmd, check=True) 
    except subprocess.CalledProcessError as e:
        print(f"Error running Freerouting: {e}")
        return
        
    # import the routed copper paths back into KiCad
    print(f"Importing SES from {ses_path}.")
    pcbnew.ImportSpecctraSES(ses_path)
    print(f"Autorouting complete! Autorouting file saved at: {ses_path}")
    
    # clean up the input DSN file
    if os.path.exists(dsn_path):
        os.remove(dsn_path)


def generate_jlcpcb_files(
        board,
        save_path,
        project_name="pcb"
        ):
    '''
    (For Top and Bottom PCBs)
    Generate JLCPCB-compatible Gerber and Drill files, 
    and package them into a ZIP archive ready for upload.
    '''
    print("Generating Gerber and Drill files for JLCPCB.")
    
    # create output folder
    output_dir = os.path.join(save_path, f"{project_name}_Gerbers")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # set up Plot Controller for Gerbers
    pctl = pcbnew.PLOT_CONTROLLER(board)
    popt = pctl.GetPlotOptions()
    
    popt.SetOutputDirectory(output_dir)
    popt.SetPlotFrameRef(False)
    popt.SetSketchPadLineWidth(pcbnew.FromMM(0.1))
    popt.SetAutoScale(False)
    popt.SetScale(1)
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(True)
    popt.SetUseGerberProtelExtensions(False)
    popt.SetUseAuxOrigin(False) 
    popt.SetSubtractMaskFromSilk(True) # Clears silkscreen off your copper pads
    
    # define all the layers JLCPCB needs except inner layers
    layers = [
        ("F_Cu", pcbnew.F_Cu, "Top Copper"),
        ("B_Cu", pcbnew.B_Cu, "Bottom Copper"),
        ("F_SilkS", pcbnew.F_SilkS, "Top Silkscreen"),
        ("B_SilkS", pcbnew.B_SilkS, "Bottom Silkscreen"),
        ("F_Mask", pcbnew.F_Mask, "Top Solder Mask"),
        ("B_Mask", pcbnew.B_Mask, "Bottom Solder Mask"),
        ("Edge_Cuts", pcbnew.Edge_Cuts, "Board Outline")
    ]

    # check if board used inner layers during autorouting. if so, add inner layers
    has_inner_tracks = any(
        track.GetLayer() in [pcbnew.In1_Cu, pcbnew.In2_Cu] for track in board.GetTracks() \
        if track.GetClass() in ['PCB_TRACK', 'PCB_ARC', 'TRACK', 'ARC'])
    has_inner_zones = any(zone.GetLayer() in [pcbnew.In1_Cu, pcbnew.In2_Cu] for zone in board.Zones())
    has_inner_copper = has_inner_tracks or has_inner_zones
    board.SetCopperLayerCount(4 if has_inner_copper else 2)
    if has_inner_copper:
        layers.extend([
            ("In1_Cu", pcbnew.In1_Cu, "Inner 1 Copper"),
            ("In2_Cu", pcbnew.In2_Cu, "Inner 2 Copper"),
        ])
    
    # generate a .gbr file for each layer
    for name, layer_id, desc in layers:
        pctl.SetLayer(layer_id)
        pctl.OpenPlotfile(name, pcbnew.PLOT_FORMAT_GERBER, desc)
        pctl.PlotLayer()
    pctl.ClosePlot()
    
    # set up Excellon Writer for Drill files (.drl)
    drlwriter = pcbnew.EXCELLON_WRITER(board)
    
    mirror = False
    minimalHeader = False
    offset = pcbnew.VECTOR2I(0, 0) # Use absolute board coordinates
    mergeNPTH = False 
    
    drlwriter.SetOptions(mirror, minimalHeader, offset, mergeNPTH)
    drlwriter.SetFormat(True) # metric format
    
    # create the drill files in the same output directory
    drlwriter.CreateDrillandMapFilesSet(pctl.GetPlotDirName(), True, False)
    
    # zip the folder for JLCPCB Upload
    zip_filename = os.path.join(save_path, f"{project_name}_JLCPCB_Production")
    shutil.make_archive(zip_filename, 'zip', output_dir)
    print(f"JLCPCB file saved at: {zip_filename}.zip")


def plot_pcb(
        board,
        save_path
        ):
    '''
    (For Top and Bottom PCBs)
    Plot and save SVGs of the top and bottom view of the PCB
    '''
    
    fig_path = os.path.join(save_path, 'figures')
    os.makedirs(fig_path)

    # initialize and configure plot controller
    pctl = pcbnew.PLOT_CONTROLLER(board)
    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(fig_path)
    popt.SetDrillMarksType(pcbnew.DRILL_MARKS_FULL_DRILL_SHAPE)
    popt.SetSkipPlotNPTH_Pads(False)
    pctl.SetColorMode(True)
    settings_manager = pcbnew.GetSettingsManager()
    popt.SetColorSettings(settings_manager.GetColorSettings("kicad-default"))

    # top view of PCB
    popt.SetMirror(False)
    pctl.OpenPlotfile("Top_View", pcbnew.PLOT_FORMAT_SVG, "Top View")
    top_layers = [pcbnew.F_Cu, pcbnew.F_SilkS, pcbnew.Edge_Cuts]
    for layer in top_layers:
        pctl.SetLayer(layer)
        pctl.SetColorMode(True)
        pctl.PlotLayer()
    pctl.ClosePlot()

    # bottom view of PCB
    popt.SetMirror(True)
    pctl.OpenPlotfile("Bottom_View", pcbnew.PLOT_FORMAT_SVG, "Bottom View")
    bottom_layers = [pcbnew.B_Cu, pcbnew.B_SilkS, pcbnew.Edge_Cuts]
    for layer in bottom_layers:
        pctl.SetLayer(layer)
        pctl.SetColorMode(True)
        pctl.PlotLayer()
    pctl.ClosePlot()
    
    print(f"Top and Bottom view SVGs successfully saved to {fig_path}")