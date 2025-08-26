# Multi-region electrophysiology custom implant algorithm

### This project is meant to algorithmically create custom implants to accommodate electrophysiological recordings across arbitrarily large numbers of brain regions.

### The premise of this algorithm is the following:
> 1. ### Given a set of EIB coordinates and a set of stereotaxic brain coordinates, the algorithm will<br>find the closest match between each EIB channel and that brain region.
> 2. ### This will create two STL files to be 3d-printed or milled. The first one ensures that each wire is at<br>the correct ML and AP stereotaxic locations (`implant.stl`). The second file ensures that the<br>DV coordinate is correct (`depth_guide.stl`).
> 3. ### The algorithm will also produce two visualizations to assist with the assembly of the implant.
> 4. ### Then, wires of your choosing (we have been using [Stablohm 650 wire](https://calfinewire.com/item/alloys/all-alloys/100187-stablohm-650-wire)) must be electrically<br>connected to the EIB and threaded through the 3d-printed implant.
> 5. ### The EIB and implant must be adhered to one another; we've been adhering them with<br>cyanoacrylate, dental cement, or metabond.
> 6. ### Once assembled, the impedance of each electrode is tested by submerging the signal and<br>ground wires into saline and running a program to test impedances.
> 7. ### Finally, the implant is surgically implanted into the subject for further recording.