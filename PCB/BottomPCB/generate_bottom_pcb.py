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
## Specify parameters ##
########################

brain_regions_csv = 'CTX_TH_HPC_Bilateral_16Ch.csv'

# Specify board and coordinate properties (in mm)
board_offset_x = 50 # location of top left corner of board in KiCad
board_offset_y = 50

board_height = 12
board_width = 14

board_offset_x += (board_width/2)
board_offset_y += (board_height/2)

board = pcbnew.GetBoard()
board.SetCopperLayerCount(4)
design_settings = board.GetDesignSettings()
design_settings.m_MinClearance = pcbnew.FromMM(0.10)
design_settings.SetBoardThickness(pcbnew.FromMM(0.8))
net_settings = design_settings.m_NetSettings
default_netclass = net_settings.GetDefaultNetclass()
default_netclass.SetClearance(pcbnew.FromMM(0.10))
default_netclass.SetTrackWidth(pcbnew.FromMM(0.15))

close_editor = False # whether or not to close the PCB editor automatically at the end

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

# Add inner vias for stereotaxic coordinates
inner_vias = utilities.add_inner_vias(
    brain_regions_csv=os.path.join('../../StereotaxCoords', brain_regions_csv),
    board=board,
    board_offset_x=board_offset_x,
    board_offset_y=board_offset_y
    )

# Match inner vias to outer through-holes
cx, cy = utilities.match_vias_holes(
    outer_holes=outer_holes,
    inner_vias=inner_vias,
    board=board)

# Label outer through-holes with channels
utilities.label_outer_holes(
    outer_holes=outer_holes,
    cx=cx,
    cy=cy,
    board=board
)

# Label inner vias with brain regions
utilities.label_inner_vias(
    brain_regions_csv=os.path.join('../../StereotaxCoords', brain_regions_csv),
    board_offset_x=board_offset_x,
    board_offset_y=board_offset_y,
    board=board
)

# Draw lines for midline, bregma, lambda
abs_bregma_y = board_offset_y
abs_lambda_y = abs_bregma_y + 4.2
b_silk = pcbnew.B_SilkS

utilities.draw_silk_line( # midline
    (board_offset_x, abs_bregma_y - 2), 
    (board_offset_x, abs_lambda_y + 2), 
    b_silk, board=board)

utilities.draw_silk_line( # bregma
    (board_offset_x - 3, abs_bregma_y), 
    (board_offset_x + 3, abs_bregma_y), 
    b_silk, board=board)

utilities.draw_silk_line( # lambda
    (board_offset_x - 3, abs_lambda_y), 
    (board_offset_x + 3, abs_lambda_y), 
    b_silk, board=board)

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
save_path = os.path.join('../../GeneratedFiles/BottomPCB', current_time)
os.makedirs(save_path)

# Run Freerouting plugin to route inner vias to outer through-holes
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
    project_name="NightCap_BottomPCB"
    )

# Plot top and bottom view of the PCB and save figures
utilities.plot_pcb(board=board, save_path=save_path)

# Generate channel_map.csv matching inner via regions to outer PTH channels
channel_map = [['Region', 'AP', 'ML', 'DV', 'Ch']]
for region, ch in zip(inner_vias, outer_holes):
    channel_map.append([region['ch'], region['ap'], region['ml'], region['dv'], ch['ch']])
with open(os.path.join(save_path, "channel_map.csv"), mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(channel_map)

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