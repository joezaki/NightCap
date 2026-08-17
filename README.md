# NightCap

> ### NightCap is a tool for constructing custom electrophysiology implants for performing multi-site electrophysiology. Given a set of stereotaxic coordinates for up to 16 brain regions, this pipeline will produce a 3D-printable implant along with a custom electrode interface board (EIB) where holes in both are stereotaxically defined.

#### *Note: NightCap was made initially for performing long-term electrophysiology for sleep studies; however, this tool can be applied as readily to any chronic electrophysiology setup.*
***

## *Procedure*
### *General Overview*

> 1.  First, create a CSV file of stereotaxic locations with the following columns: `['Region', 'AP', 'ML', 'DV', 'Type']`.
> 1. Type should be one of `['LFP', 'GND', 'REF', 'EEG', 'EMG']`.
> 1. Save this file in the `StereotaxCoords` folder.
> 1. Proceed to `Implant` instructions below to construct the 3D-printable implant.
> 1. Proceed to `PCB`, `Bottom PCB`, and `Top PCB` instructions to construct the bottom and top PCBs.
> 1. Proceed to `Assembly` to put everything together.<br>
> *Note: Images below are examples from running the pipeline on the CSV provided in the repo: `/StereotaxCoords/CTX_TH_HPC_Bilateral_16Ch.csv`*

***

### *Implant*
> 1. In the `Implant` sub-folder, open the `generate_implant.py` file in a text editor. In the `Specify parameters` section, update `brain_regions_csv` with the filename of your stereotaxic coordinates file. Modify any other parameters of interest here.
> 1. Open a terminal window, navigate to the `NightCap` folder: `cd ~/path/to/NightCap`
> 1. Create the conda environment: `conda env create -f environment.yml`<br>*Note: If you do not have conda installed on your computer, navigate to [anaconda](anaconda.org) in a browser and install anaconda first.*
> 1. Activate environment: `source activate nightcap`
> 1. Execute script: `python generate_implant.py`. It may take a few minutes to run. The terminal window will print statements as the pipeline progresses.
> 1. A folder called `GeneratedFiles/Implant` should have been created. Check inside this folder for a folder with the current time. Inside this folder should be:
> > - `implant.stl` & `depth_guide.stl` (3D-printable STL files)
> > - `implant.scad` & `depth_guide.scad` (SCAD files for constructing STL files)
> > - `regions.csv` (Original stereotaxic coordinates CSV)
> > - `implant_depth_guide.html` (interactive visualization of the stl files for the implant and depth guide)
> > - `2d_implant.html` & `3d_implant.html` (interactive visualizations of the implant mapping)
> > - `3d_implant_animation.gif` (GIF of the 3D rotating implant for presentations)<br>

<div align="center">
    <img src="./images/implant/implant_depth_guide.svg" alt="implant_depth_guide" width="700" /><br>
    <img src="./images/implant/2d_implant.svg" alt="2d_implant" width="700" /><br>
    <img src="./images/implant/3d_implant.svg" alt="3d_implant" width="700" /><br>
    <img src="./images/implant/3d_implant_animation.gif" alt="3d_implant_animation" width="700" />
</div>

***

### *PCB*
> 0. Only perform the following two steps prior to first use of this pipeline:
> 1. For PCB construction, we will use the KiCad software. [Install KiCad here.](kicad.org)
> 1. After installing KiCad, install the Freerouting plugin:
> > - Open KiCad
> > - `Tools -> Plugin and Content Manager`
> > - Find "Freerouting" and install.
> > - Click "Apply Pending Changes"
> > - [Install Java here.](https://adoptium.net/temurin/releases)
> > - After installation, restart KiCad.

***

### *Bottom PCB*
> 1. In the `BottomPCB` subfolder, open `generate_bottom_pcb.py` file in a text editor. In the `Specify parameters` section, update `brain_regions_csv` with the filename of your stereotaxic coordinates file. Modify any other parameters of interest here.
> 1. In KiCad, open project by clicking on `.../NightCap/PCB/BottomPCB/BottomPCB.kicad_pro`
> 1. Click on PCB Editor. A blank window should pop up.
> 1. `Tools -> Scripting Console`
> 1. Execute script: `exec(open('./generate_bottom_pcb.py').read())`
> 1. A folder should have been created in `GeneratedFiles/BottomPCB/` with the current time. Inside this folder should be:
> > - `NightCap_BottomPCB_JLCPCB_Production.zip` (main file to upload to JLCPCB for PCB construction)
> > - `NightCap_BottomPCB_Gerbers/` (folder with gerber files for PCB construction)
> > - `channel_map.csv` (mapping between each brain region and the EIB channel)
> > - `autoroute.ses` (file with autorouting track data)
> > - `figures/` (folder with visualizations of PCB)<br>

<div align="center">
    <img src="./images/bottom_pcb/BottomPCB-top_view.svg" alt="bottom_pcb_top_view" width="350" />
    <img src="./images/bottom_pcb/BottomPCB-bottom_view.svg" alt="bottom_pcb_bottom_view" width="350" />
</div>

***

### *Top PCB*
> 1. In the `TopPCB` subfolder, open `generate_top_pcb.py` file in a text editor. In the `Specify parameters` section, update `which_connector` to be one of `['molex', 'omnetics']`. Modify any other parameters of interest here.
> 1. In KiCad, open project by clicking on `.../NightCap/PCB/TopPCB/TopPCB.kicad_pro`
> 1. Click on PCB Editor. A blank window should pop up.
> 1. `Tools -> Scripting Console`
> 1. Execute script: `exec(open('./generate_top_pcb.py').read())`
> 1. A folder should have been created in `GeneratedFiles/TopPCB/` with the current time. Inside this folder should be:
> > - `NightCap_TopPCB_JLCPCB_Production.zip` (main file to upload to JLCPCB for PCB construction)
> > - `NightCap_TopPCB_Gerbers/` (folder with gerber files for PCB construction)
> > - `NightCap_TopPCB_BOM.csv` (file for bill of materials for connector (molex or omnetics))
> > - `NightCap_TopPCB_positions.csv` (file placement position for connector onto PCB)
> > - `autoroute.ses` (file with autorouting track data)
> > - `figures/` (folder with visualizations of PCB)<br>

<div align="center">
    <img src="./images/top_pcb/TopPCB-top_view.svg" alt="top_pcb_top_view" width="350" />
    <img src="./images/top_pcb/TopPCB-bottom_view.svg" alt="top_pcb_bottom_view" width="350" />
</div>

***

### *Assembly*
> 0. Once implant, depth guide, top PCB, and bottom PCB have been created, the whole implant needs to be assembled.
> 1. First, take wire of your choosing (we have been using [Stablohm 650 wire](https://calfinewire.com/item/alloys/all-alloys/100187-stablohm-650-wire) for LFP wires and [PFA-Coated Silver Wire 786000](https://www.a-msystems.com/p-796-pfa-coated-silver-wire.aspx) for EEG and EMG wires).
> 1. Cut each wire to ~20mm long using sharp scissors, and strip 1mm of insulation off one end of each wire. This side will connect to the bottom PCB.
> 1. Feed header pins into each outer via on the bottom PCB and solder into place.
> 1. Attach implant onto bottom PCB.
> 1. Secure depth guide onto the implant. Look top down through the bottom PCB to make sure that all the holes align.
> 1. Feed each wire through the holes in the bottom PCB. They should feed cleanly through the bottom PCB, implant, and depth guide. Solder them in place.
> 1. Line up the top PCB over the bottom PCB using the header pins. Solder the pins in place.
> 1. At this point, the impedance of each electrode is tested by submerging the signal and ground wires into saline and running a program to test impedances.
> 1. Snip the wires to length at the point at which they exit the depth guide, using sharp scissors.
> 1. Remove the depth guide.
> 1. The implant is now ready for implantation. Finally, the implant is surgically implanted into the subject for recording.

### Happy recording! :sparkles: