import os
import sys

# import for DYNA
from ansys.dyna.core import keywords as kwd
from ansys.dyna.core.pre.dynabase import (
    SolidPart,
    DynaBase,
    Part,
)
from ansys.dyna.core.pre import launch_dynapre
from ansys.dyna.core.pre.dynamech import (
    AnalysisType,
    DynaMech,
    SolidPart,
    Part,
    SolidFormulation
)
from ansys.dyna.core.pre.misc import check_valid_ip
from enum import Enum

# Use 'localhost' unless an IP is provided as a command-line argument
hostname = "localhost"
if len(sys.argv) > 1 and check_valid_ip(sys.argv[1]):
    hostname = sys.argv[1]

# Connect to the PyDYNA pre-processor service
solution = launch_dynapre(ip=hostname)

Current_Directory = os.path.dirname(os.path.abspath(__file__))
Input_LatticeFile = os.path.join(Current_Directory, "WingLattice_v2(Test).k")
Output_LatticeFile = os.path.join(Current_Directory, "WingLattice_v2(Test)_final.k")

# ---------------------------------------------------------
# FIX 1: Material Definition
# Removed trailing commas to ensure these are treated as numbers, not tuples
# ---------------------------------------------------------
mat_1 = kwd.Mat020(mid=1)
mat_1.ro = 1.25e-9
mat_1.e = 2.0
mat_1.pr = 0.35
mat_1.sigy = 0.05
mat_1.etan = 0.0

# ---------------------------------------------------------
# FIX 2: Part Definition
# Replaced undefined 'create_section_solid' with 'SolidPart' class
# ---------------------------------------------------------
# Create a SolidPart with ID 1 (Must match the Part ID in your input .k file)
DynaBase.__init__(solution)  # Set the stub for DynaBase to the current solution
solid = SolidPart(Part(1))
# Assign the material defined above
solid.material = mat_1
El_form = SolidFormulation(1)
solid.set_element_formulation(El_form)
("lattice",1, 10)
# Set the element formulation (ELFORM) to 10 
# (This matches the '10' from your previous code snippet)
# solid.section.elform = 10

# Open the existing .k file containing the geometry
solution.open_files([Input_LatticeFile])

###############################################################################
# Define Analysis and Add Part
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Create the main mechanical analysis object (DynaMech)
wing_analysis = DynaMech(AnalysisType.NONE)
solution.add(wing_analysis)

# Add the defined part (Lattice) to the analysis model
wing_analysis.parts.add(solid)

###############################################################################
# Save the new LS-DYNA input file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

solution.set_file_name(Output_LatticeFile)
serverpath = solution.save_file()

serveroutfile = "/".join((serverpath, os.path.basename(Output_LatticeFile)))
downloadpath = os.path.dirname(Output_LatticeFile)

if not os.path.exists(downloadpath):
    os.makedirs(downloadpath)

solution.download(serveroutfile, Output_LatticeFile)

print(f"Successfully saved and downloaded the final LS-DYNA input file to: {Output_LatticeFile}")
