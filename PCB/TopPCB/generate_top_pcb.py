import os
import pcbnew
import csv
from datetime import datetime
import wx
import importlib
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
design_settings = board.GetDesignSettings()
design_settings.m_MinClearance = pcbnew.FromMM(0.10)
design_settings.SetBoardThickness(pcbnew.FromMM(0.8))
net_settings = design_settings.m_NetSettings
default_netclass = net_settings.GetDefaultNetclass()
default_netclass.SetClearance(pcbnew.FromMM(0.10))
default_netclass.SetTrackWidth(pcbnew.FromMM(0.15))

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
rotation_deg = (
    90 if which_connector=='omnetics' else \
    270 if which_connector=='molex' else \
    Exception('Invalid connector type.')
)
connector = utilities.place_footprint(
    board,
    library_path,
    footprint_name,
    board_offset_x,
    board_offset_y + 2.5,
    rotation_deg=rotation_deg,
    reference="C1"
)
connector_pads = utilities.get_pad_location_info(connector)
outer_holes_dict = {
    hole["ch"]: hole
    for hole in outer_holes
}

# Match inner connector pins to outer through-holes
pairs = utilities.load_pin_to_hole_matching_csv(
    filename=f"../Coordinates/PTH_To_Pin_{which_connector.capitalize()}.csv",
    holes=outer_holes_dict,
    pins=connector_pads
)
for pin, hole, net_suffix in pairs:
    net_name = f"Net_{net_suffix}"
    net = board.FindNet(net_name)

    if net is None:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)

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

# Draw magnet outlines
utilities.draw_magnet_circle( # top left magnet
    center_x=board_offset_x - 3,
    center_y=board_offset_y - 3.50,
    radius=1.5875,
    board=board,
    b_silk=b_silk
    )
utilities.draw_magnet_circle( # bottom right magnet
    center_x=board_offset_x + 3,
    center_y=board_offset_y + 7.5,
    radius=1.5875,
    board=board,
    b_silk=b_silk
    )

# Remove reference labels to declutter PCB
for module in board.Footprints():
    module.Reference().SetVisible(False)
pcbnew.Refresh()

# Create save path
current_time = str(datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
save_path = os.path.join('../../GeneratedFiles/TopPCB', current_time)
os.makedirs(save_path)

# Run Freerouting plugin to route inner pins to outer through-holes
utilities.auto_route_board(save_path=save_path)
pcbnew.Refresh()

#%%
#########################################
## Generate JLCPCB files and PCB plots ##
#########################################

# Generate gerber and drl for printing PCBs
utilities.generate_jlcpcb_files(
    board,
    save_path=save_path,
    project_name="NightCap_TopPCB"
    )

# generate BOM and placement files
with open(os.path.join(save_path, "NightCap_TopPCB_BOM.csv"), mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    bom = [
        ['Comment', 'Designator', 'Footprint', 'LCSC Part #'],
        [footprint_name, 'C1', footprint_name, '']
    ]
    writer.writerows(bom)

with open(os.path.join(save_path, "NightCap_TopPCB_positions.csv"), mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    connector_placement = [
        ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'],
        ['C1', board_offset_x, board_offset_y, rotation_deg, 'Top']
    ]
    writer.writerows(connector_placement)

# Plot top and bottom view of the PCB and save figures
utilities.plot_pcb(board=board, save_path=save_path)

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