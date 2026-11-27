import os
import pcbnew
import csv
from datetime import datetime
import wx
import importlib
from collections import defaultdict
import sys
sys.path.append('..')
import utilities
importlib.reload(utilities)

#%%
########################
## Specify Parameters ##
########################

which_connector = 'molex' # one of 'molex' or 'omnetics'

# Specify board and coordinate properties (in mm)
board_offset_x = 50 # location of top left corner of board in KiCad
board_offset_y = 50

board_height = 12
board_width = 14

board_offset_x += (board_width/2)
board_offset_y += (board_height/2)

board = pcbnew.GetBoard()
board.SetCopperLayerCount(2)
base_clearance = 0.15 if which_connector == 'omnetics' else 0.12
board_rules = dict(
    clearance_mm=base_clearance,
    track_width_mm=0.15,
    via_diameter_mm=0.45,
    via_drill_mm=0.20,
    edge_clearance_mm=0.35,
    board_thickness_mm=0.8,
    ref_net_name="Net_REF",
    ref_clearance_mm=base_clearance,
    ref_track_width_mm=0.20,
)
ref_nc = utilities.configure_board_rules(
    board,
    **board_rules
)

close_editor = True # whether or not to close the PCB editor automatically at the end

#%%
#################################
## Generate PCB and add labels ##
#################################

pcbnew.Refresh()

# Draw edge cuts of PCB
utilities.draw_csv_outline(
    csv_path='../Coordinates/EdgeCuts.csv',
    board=board,
    board_offset_x=board_offset_x,
    board_offset_y=board_offset_y,
    line_thickness=0.15
)

# Add through-holes around PCB
outer_holes = utilities.add_outer_holes(
    outer_holes_csv='../Coordinates/OuterHoles.csv',
    board=board,
    board_offset_x=board_offset_x,
    board_offset_y=board_offset_y
    )

# Add connector (Molex or Omnetics)
library_path = "./NightCap.pretty"
connectors_dict = {
    'molex'    : "CON_513382474",
    'omnetics' : "CONN-SMD_18P-P0.64_A79042-001"
}
footprint_name = connectors_dict[which_connector]
if which_connector == 'omnetics':
    rotation_deg = 90
elif which_connector == 'molex':
    rotation_deg = 270
else:
    raise Exception('Invalid connector type.')

connector_x = board_offset_x
connector_y = board_offset_y + 2.5
connector = utilities.place_footprint(
    board,
    library_path,
    footprint_name,
    connector_x,
    connector_y,
    rotation_deg=rotation_deg,
    reference="J1"
)
connector_pads = utilities.get_pad_location_info(connector)
outer_holes_by_ch = defaultdict(list)
for hole in outer_holes:
    raw_ch = hole["ch"].strip()
    key = raw_ch.upper() if raw_ch.upper() in ("GND", "REF") else raw_ch
    outer_holes_by_ch[key].append(hole)

# Match inner connector pins to outer through-holes
pairs = utilities.load_pin_to_hole_matching_csv(
    filename=f"../Coordinates/PTH_To_Pin_{which_connector.capitalize()}.csv",
    holes=outer_holes_by_ch,
    pins=connector_pads
)
for pin, hole, _ in pairs:
    raw_ch = hole["ch"].strip()
    ch_norm = raw_ch.upper() if raw_ch.upper() in ("GND", "REF") else raw_ch
    net_name = f"Net_{ch_norm}"
    net = utilities.get_or_create_net(board, net_name)

    pin['obj'].SetNet(net)
    hole['obj'].SetNet(net)

    print(f"Inner connector pin '{pin['ch']}' mapped to outer PTH '{hole['ch']}' -> {net_name}")

cx = sum(p["x"] for p in outer_holes) / len(outer_holes)
cy = sum(p["y"] for p in outer_holes) / len(outer_holes)

# Label outer through-holes with channels
utilities.label_outer_holes(
    outer_holes=outer_holes,
    cx=cx,
    cy=cy,
    board=board
)
b_silk = pcbnew.B_SilkS

# Draw magnet outlines in the 4 corners
for magnet_coords in [
    [-3, -3.5], # top left
    [-3,  7.5], # top right
    [ 3, -3.5], # bottom left
    [ 3,  7.5]  # bottom right
]:    
    utilities.draw_magnet_circle(
        center_x=board_offset_x + magnet_coords[0],
        center_y=board_offset_y + magnet_coords[1],
        radius=1.5875,
        board=board,
        b_silk=b_silk,
        add_keepout=True,
        keepout_layers=[pcbnew.B_Cu]
        )

# Remove reference labels to declutter PCB
for module in board.Footprints():
    module.Reference().SetVisible(False)

# Tie metallic mounting/shield pads on J1 to Net_GND so they don't float
gnd_net = utilities.get_or_create_net(board, "Net_GND")
for pad in connector.Pads():
    # Skip pads already mapped via CSV and non-plated alignment holes (NPTH)
    if pad.GetNetCode() != 0 or pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
        continue

    pad_num = pad.GetNumber().strip()
    is_mechanical = (pad_num == "" or not pad_num.isdigit())

    if is_mechanical:
        pad.SetNet(gnd_net)
        print(f"Connector mechanical/shield pad '{pad_num or '<unnumbered>'}' -> Net_GND")
    else:
        print(
            f"Note: Unmapped numeric pad '{pad_num}' on J1 left floating "
            "(if this is a mounting nail, map it to GND in the CSV or add it below)."
        )

# assign board rules before routing
utilities.assign_ref_netclass(board, ref_net_name="Net_REF", ref_nc=ref_nc)

pcbnew.Refresh()

# Create save path
current_time = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
save_path = os.path.join('../../GeneratedFiles/TopPCB', current_time)
os.makedirs(save_path)

# Run Freerouting plugin to route inner pins to outer through-holes
utilities.auto_route_board(save_path=save_path)

# Save copy of configured kicad_pcb in save_path
pcb_path = os.path.join(save_path, "NightCap_TopPCB.kicad_pcb")
pcbnew.SaveBoard(pcb_path, board)

# Switch to 4-layer board for adding ground plane
final_board = pcbnew.LoadBoard(pcb_path)
final_board.SetCopperLayerCount(4)
final_ref_nc = utilities.configure_board_rules(final_board, **board_rules)
utilities.assign_ref_netclass(final_board, ref_net_name="Net_REF", ref_nc=final_ref_nc)
final_board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(0.8))
final_board.GetDesignSettings().m_CopperEdgeClearance = pcbnew.FromMM(0.30)
for fp in final_board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() == "Net_REF" and pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            pad.SetLocalClearance(pcbnew.FromMM(board_rules["ref_clearance_mm"] + 0.02))
pcbnew.SaveBoard(pcb_path, final_board)

# Inject ground planes into the inner layers
utilities.add_ground_plane(final_board, pcbnew.In1_Cu, net_name="Net_GND")
utilities.add_ground_plane(final_board, pcbnew.In2_Cu, net_name="Net_GND")
filler = pcbnew.ZONE_FILLER(final_board)
filler.Fill(final_board.Zones())
pcbnew.SaveBoard(pcb_path, final_board)

pcbnew.Refresh()

# Run DRC to ensure no errors up until this point
utilities.run_DRC(
    save_path=save_path,
    pcb_path=pcb_path
    )

#%%
#########################################
## Generate JLCPCB files and PCB plots ##
#########################################

# Generate gerber and drl for printing PCBs
utilities.generate_jlcpcb_files(
    final_board,
    save_path=save_path,
    project_name="NightCap_TopPCB"
    )

# generate BOM and placement files
with open(os.path.join(save_path, "NightCap_TopPCB_BOM.csv"), mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    bom = [
        ['Comment', 'Designator', 'Footprint', 'LCSC Part #'],
        [footprint_name, 'J1', footprint_name, '']
    ]
    writer.writerows(bom)

with open(os.path.join(save_path, "NightCap_TopPCB_positions.csv"), mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    connector_placement = [
        ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'],
        ['J1', f"{connector_x:.4f}mm", f"{-connector_y:.4f}mm", rotation_deg % 360, 'Top']
    ]
    writer.writerows(connector_placement)

# Plot top and bottom view of the PCB and save figures
utilities.plot_pcb(board=final_board, save_path=save_path)

# Close PCB editor window
for window in wx.GetTopLevelWindows():
    if "PCB Editor" in window.GetTitle() or "pcbnew" in window.GetTitle().lower():
        if close_editor:
            window.Destroy()
pcbnew.Refresh()

# Delete kicad_prl preferences file
kicad_prl_path = [x for x in os.listdir(os.getcwd()) if x.endswith('kicad_prl')]
if len(kicad_prl_path) > 0:
    os.remove(os.path.join(os.getcwd(), kicad_prl_path[0]))