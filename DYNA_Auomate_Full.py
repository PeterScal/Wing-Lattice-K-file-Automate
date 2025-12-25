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