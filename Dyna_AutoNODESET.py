from ansys.dyna.core import Deck
from ansys.dyna.core import keywords as kwd
import lsdyna_mesh_reader as mesh
import os

# Define file paths
Current_Directory = os.path.dirname(os.path.abspath(__file__))
Ls_Dyna_Folder = os.path.dirname(Current_Directory)

# Path to the file containing the NODE definitions
Input_LatticeFile = os.path.join(Ls_Dyna_Folder,"LS-DYNA", "WingLattice_v2.k") 

# New Deck using mesh reader to find nodes on surface planes
mesh_deck = mesh.Deck(Input_LatticeFile)
node_section = mesh_deck.node_sections[0]
print(node_section)

# Test reading .k file
print(node_section.coordinates)
print(node_section.nid)

# Configuration for the surface plane for faom to lattice connection
x_target = 76.0
y_min, y_max = -3.897, 17.392
z_min, z_max = 0.1307, 101.554
tolerance = 0.1 

# Access coordinates and NIDs from the reader
coords = node_section.coordinates
nids = node_section.nid

# Create booleans for each dimension based on your targets
nodes_x = (coords[:, 0] >= x_target - tolerance) & (coords[:, 0] <= x_target + tolerance)
nodes_y = (coords[:, 1] >= y_min) & (coords[:, 1] <= y_max)
nodes_z = (coords[:, 2] >= z_min) & (coords[:, 2] <= z_max)

# Combine booleans to find nodes satisfying all criteria
full_nodes = nodes_x & nodes_y & nodes_z

# Extract the resulting Node IDs
target_node_ids_latfoam = nids[full_nodes].tolist()

# List nodes found and used for the node set
print(f"Found {len(target_node_ids_latfoam)} nodes.")
print(target_node_ids_latfoam)

#--------------------------------------------------------------------------------------------------------------------------------------
# Configuration for the surface plane for lattice to UAV Body connection
x_max = 76.102
x_min = 0.047
z_target = 0.3024
y_min = -5.328
y_max = 17.908

# Create booleans for each dimension based on your targets
nodes_z = (coords[:, 2] >= z_target - tolerance) & (coords[:, 2] <= z_target + tolerance)
nodes_y = (coords[:, 1] >= y_min) & (coords[:, 1] <= y_max)
nodes_x = (coords[:, 0] >= x_min) & (coords[:, 0] <= x_max)

# Combine booleans to find nodes satisfying all criteria
full_nodes = nodes_x & nodes_y & nodes_z

# Extract the resulting Node IDs
target_node_ids_latUAV = nids[full_nodes].tolist()

# List nodes found and used for the node set
print(f"Found {len(target_node_ids_latUAV)} nodes.")
print(target_node_ids_latUAV)

#--------------------------------------------------------------------------------------------------------------------------------------

# Add new node set to deck:
node_set_foam = kwd.SetNodeList(sid=1)
node_set_foam.nodes = target_node_ids_latfoam

# Add new node set to deck:
node_set_uav = kwd.SetNodeList(sid=2)
node_set_uav.nodes = target_node_ids_latUAV

# Extend deck with new keywords



