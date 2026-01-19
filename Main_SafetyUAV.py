#Main File for running code

from CAD_mod import set_lattice_ratio
from ntop_mod import set_ntop_params
from Dyna_AutoMATs import setup_material_section_part
from Dyna_AutoRUN import run_Ls_Dyna
from Dyna_AutoNODESET import setup_nodesets_LatFoam, setup_nodesets_LatUAV, setup_nodesets_FoamLat_SegmentSet, setup_nodesets_FoamUAV
import numpy as np
import os, json

' Define all paths for files going foward here first '
#Directory Setup
Current_Directory = os.path.dirname(os.path.abspath(__file__))

# Ntop and JSON file paths
Paramter_list_Name = os.path.join(Current_Directory, "Parameter_list.json")
Input_Template_Name = os.path.join(Current_Directory, "input_template.json")
Output_Template_Name = os.path.join(Current_Directory, "output_template.json")

# LS prepost Path to the files:
Ls_Dyna_Folder = os.path.dirname(Current_Directory)
Input_LatticeFile = os.path.join(Ls_Dyna_Folder,"LS-DYNA", "WingLattice_v2.k")
Input_FoamFile = os.path.join(Ls_Dyna_Folder,"LS-DYNA", "Wing_FoamHalf.k")

# Input_SystemFile = os.path.join(Ls_Dyna_Folder,"LS-DYNA", "WingLattice_System.k")
# Move up one level to D:\Modified_Wing
parent_dir = os.path.dirname(Current_Directory)

# Go into the LS-DYNA folder to find the .k file
input_dir = os.path.join(parent_dir, "LS-DYNA")
input_file = os.path.join(input_dir, "WingLattice_v2.k")

#---------------- CAD Modification Section ------------------------------------------------------------------------------------------
' Requires all CAD models to be up and running before running this script '

# List of Target names and dimensions to modify
Title_list = ["Wing_SD7080_12in_Lattice", "Wing_SD7080_12in_Foam", "Wing_SD7080_12in_Base"]
Dimension_list = ["D2@Sketch2", "D2@Sketch2", "D1@Sketch1"]
stepfile_path_list = [
      r"D:\Modified_Wing\CAD\Wing_SD7080_12in_Lattice.STEP",
      r"D:\Modified_Wing\CAD\Wing_SD7080_12in_Foam.STEP",
      r"D:\Modified_Wing\CAD\Wing_SD7080_12in_Base.STEP"
    ]

#Set New Lattice Ratio from JSON
with open(Paramter_list_Name, "r") as f1:
        data_1 = json.load(f1)
new_value_inches = data_1[3]["Data"][0]["Lattice_Ratio"][0]

# Running CAD modification for each file
for i in range(len(Title_list)):
    current_title = Title_list[i]
    dimensionName = Dimension_list[i]
    stepfile = stepfile_path_list[i] 
    
    set_lattice_ratio(current_title, dimensionName, new_value_inches, stepfile)

#---------------- nTop Modification Section ------------------------------------------------------------------------------------------

# Load input template 
with open(Input_Template_Name , "r") as f:
    data = json.load(f)

# ntop function
set_ntop_params(Current_Directory, Input_Template_Name, Output_Template_Name, data, data_1)


#---------------- Ls-PrePost setup Part Definition Section -------------------------------------------------------------------------

' First material properties for lattice and foam'
# Class Definaitions Lattice:
class Lattice_obj1:
     pass
class Lattice_obj2:
     pass

# Lattcie Material setting
Lattice_SetMaterial = Lattice_obj1()
Lattice_SetMaterial.id = 1
Lattice_SetMaterial.E = 1.0  
Lattice_SetMaterial.ro = 1.25e-9
Lattice_SetMaterial.sigy = 0.05
Lattice_SetMaterial.pr = 0.35
Lattice_SetMaterial.etan = 0.2

#Lattice Section and part ID Setting
Lattice_SetSection = Lattice_obj2()
Lattice_SetSection.id = 1
Lattice_SetSection.elform = 10
Lattice_SetSection.partid = 1

# Class definitions foam:
class Foam_obj1:
     pass
class Foam_obj2:
     pass

# Lattcie Material setting
Foam_SetMaterial = Foam_obj1()
Foam_SetMaterial.id = 7
Foam_SetMaterial.E = 0.08 
Foam_SetMaterial.ro = 8e-8
Foam_SetMaterial.pr = 0
Foam_SetMaterial.damp = 0.1
Foam_SetMaterial.tsc = 0.008

#Lattice Section and part ID Setting
Foam_SetSection = Foam_obj2()
Foam_SetSection.id = 7
Foam_SetSection.elform = 10
Foam_SetSection.partid = 7

# Setting Material, Section and Part info for lattice and foam
setup_material_section_part(Input_LatticeFile, Lattice_SetMaterial, Lattice_SetSection, Ls_Dyna_Folder)
setup_material_section_part(Input_FoamFile, Foam_SetMaterial, Foam_SetSection, Ls_Dyna_Folder)


#---------------- Ls-PrePost setup NODE and SEGMENT SETs Definition Section -------------------------------------------------------------------------

# Configuration for the surface plane for lattice to Foam connection
x_target = new_value_inches * 25.4  #Convert to mm
y_min, y_max = -3.897, 17.392
z_min, z_max = 0.1307, 101.554
tolerance = 0.1 

setup_nodesets_LatFoam(Input_LatticeFile, x_target, y_min, y_max, z_min, z_max, tolerance)

# # Configuration for the surface plane for Lattice to UAV connection
x_max = new_value_inches * 25.4  #Convert to mm
x_min = 0.047
z_target = 0.3024
y_min = -5.328
y_max = 17.908
tolerance = 0.1 

setup_nodesets_LatUAV(Input_LatticeFile, x_max, x_min, z_target, y_min, y_max, tolerance)


# Configuration for the surface plane for Foam to Lattice connection
x_target = (new_value_inches + 0.08) * 25.4  #Convert to mm
y_min, y_max = -7, 20
z_min, z_max = 1, 101.554
tolerance = 0.5

setup_nodesets_FoamLat_SegmentSet(Input_FoamFile, x_target, y_min, y_max, z_min, z_max, tolerance)


# # Configuration for the surface plane for Foam to UAV connection
x_max = 12 * 25.4  #Convert to mm
x_min = (new_value_inches + 0.08) * 25.4
z_target = 0.3024
y_min = -5.328
y_max = 17.908
tolerance = 0.1 

setup_nodesets_FoamUAV(Input_FoamFile, x_max, x_min, z_target, y_min, y_max, tolerance)

#---------------- Ls-Dyna Run Simulation ----------------------------------------------------------------------------------------------------
run_Ls_Dyna(input_dir, input_file)

