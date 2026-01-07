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



#Pipeline

from ansys.dyna.core import Deck
from ansys.dyna.core import keywords as kwd
import os

# Define file paths
Current_Directory = os.path.dirname(os.path.abspath(__file__))
Input_LatticeFile = os.path.join(Current_Directory, "WingLattice_system.k")
Output_LatticeFile = os.path.join(Current_Directory, "WingLattice_v2_updated.k")

# Load your existing mesh
deck = Deck(Input_LatticeFile)
deck.import_file(Input_LatticeFile)

# Adding New Lattice
lattice_include = kwd.IncludeFile(filename='WingLattice_v2.k')
deck.append(lattice_include)

# Part Variables:
part_lattice = kwd.Part(1)
part_Dummy_Head = kwd.Part(2)
part_Base = kwd.Part(3)
part_SupportBar = kwd.Part(4)
part_Acclerator = kwd.Part(5)
part_Other_Foam_Half = kwd.Part(7)
part_UAV_Body = kwd.Part(11)
part_Spring = kwd.Part(100)

# Define coordinate system
cs_1 = kwd.DefineCoordinateSystem(cid=1)
cs_1.xl = 1.0
cs_1.yp = 1.0

# Set Node List: Defines a set of nodes by ID
node_set = kwd.SetNodeList(sid=10)
node_set.nodes = [101, 102, 103, 104] # List of Node IDs

# Set Segment: Defines a set of segments (surfaces)
# Each segment usually consists of 4 nodes (n1, n2, n3, n4)
seg_set = kwd.SetSegment(sid=20)
seg_set.segments = [
    [1, 2, 3, 4], # Segment 1 nodes
    [5, 6, 7, 8]  # Segment 2 nodes
]

# Define initial velocity for Lattice
init_vel = kwd.InitialVelocityGeneration()
init_vel.id = part_lattice.parts["pid"][1]
init_vel.styp = 2
init_vel.vx = -10 # mm/s
init_vel.icid = cs_1.cid

# Define initial velocity for Lattice
Foam_init_vel = kwd.InitialVelocityGeneration()
Foam_init_vel.id = part_Other_Foam_Half.parts["pid"][7]
Foam_init_vel.styp = 2
Foam_init_vel.vx = -10 # mm/s
Foam_init_vel.icid = cs_1.cid

# Define initial velocity for Rigid Body (UAV Body)
Rig_init_vel = kwd.InitialVelocityRigidBody()
Rig_init_vel.id = part_UAV_Body.parts["pid"][11]
Rig_init_vel.vx = -10 # mm/s
Rig_init_vel.icid = cs_1.cid

# Contact General of all parts
Part_set = kwd.SetPartList(sid=1, parts=[1,2,7,11])
Auto_Gen_Contact = kwd.ContactAutomaticGeneral()

# Tied Nodes to Surface Contact
tied_contact = kwd.ContactTiedNodesToSurface()
tied_contact.ssid = 10   # Slave Set ID (Node Set)
tied_contact.msid = 20   # Master Set ID (Segment Set)
tied_contact.sstyp = 4   # Slave type (Node List)
tied_contact.mstyp = 0   # Master type (Segment Set)

# Automatic Single Surface Contact
# Often used for self-contact within a part or part set
single_surface = kwd.ContactAutomaticSingleSurface()
single_surface.ssid = 1  # Slave Set ID (often a Part Set ID)
single_surface.sstyp = 2 # Slave type (Part Set

# Boundary SPC Set (Single Point Constraint)
spc_set = kwd.BoundarySpcSet()
spc_set.nsid = 10  # Node Set ID to be constrained
spc_set.cid = 0    # Coordinate system ID
spc_set.doctx = 1  # 1=fixed, 0=free for X translation
spc_set.docty = 1  # Fixed for Y translation
spc_set.doctz = 1  # Fixed for Z translation

# Constrained Commands
# Connects a set of nodes to a rigid body
extra_nodes = kwd.ConstrainedExtraNodesSet()
extra_nodes.pid = 11     # Part ID of the Rigid Body (UAV Body)
extra_nodes.nsid = 10    # Node Set ID

# Constrained Rigid Bodies
rigid_merge = kwd.ConstrainedRigidBodies()
rigid_merge.pidm = 11    # Master Rigid Body Part ID
rigid_merge.pids = 5     # Slave Rigid Body Part ID

# Control Termination keyword
control_term = kwd.ControlTermination(endtim=8.00000e-5, dtmin=0.001)

# Database Binary D3Plot
# Controls the frequency of result output files
d3plot = kwd.DatabaseBinaryD3plot()
d3plot.dt = 1.0e-6  # Time interval between outputs
# Append these keywords to the deck and write the file
# Append all new keywords to the deck
deck.extend([
    node_set, 
    seg_set, 
    tied_contact, 
    single_surface, 
    extra_nodes, 
    rigid_merge, 
    spc_set, 
    d3plot,
    control_term
])

# Create LS-DYNA input deck
deck_string = deck.write()
with open(Input_LatticeFile, "w") as file_handle:
    file_handle.write(deck_string)