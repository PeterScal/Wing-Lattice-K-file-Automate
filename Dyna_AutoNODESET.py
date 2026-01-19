from ansys.dyna.core import Deck
from ansys.dyna.core import keywords as kwd
import lsdyna_mesh_reader as mesh
import os, sys
import numpy as np
import pandas as pd


def setup_nodesets_LatFoam(Input_File, x_target, y_min, y_max, z_min, z_max, tolerance):

    # New Deck using mesh reader to find nodes on surface planes
    mesh_deck = mesh.Deck(Input_File)
    node_section = mesh_deck.node_sections[0]
    print(node_section)

    # Test reading .k file
    print(node_section.coordinates)
    print(node_section.nid)

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

    # delete old deck and any open existant of it and Load existing deck:
    del mesh_deck, node_section

    deck = Deck(Input_File)
    deck.import_file(Input_File)

    # Add new node set to deck:
    node_set_foam = kwd.SetNodeList(sid=1)
    node_set_foam.nodes = target_node_ids_latfoam

    # Check if node sets already exist
    nodesests = list(deck.get_kwds_by_type('SET_NODE_LIST'))
    if nodesests == True:
        print('Node sets already exist in the deck. Check keywoprd notepad.')
    else:
        #Extend deck with new keywords if not
        deck.extend([node_set_foam])
        print('Node sets added successfully.')
        # Create LS-DYNA input deck

        deck_string = deck.write()
        
        del deck

        with open(Input_File, "w") as file_handle:
            file_handle.write(deck_string)

    # Extend deck with new keywords


#--------------------------------------------------------------------------------------------------------------------------------------
# Configuration for the surface plane for lattice to UAV Body connection
def setup_nodesets_LatUAV(Input_File, x_max, x_min, z_target, y_min, y_max, tolerance):

    # New Deck using mesh reader to find nodes on surface planes
    mesh_deck = mesh.Deck(Input_File)
    node_section = mesh_deck.node_sections[0]
    print(node_section)

    # Test reading .k file
    print(node_section.coordinates)
    print(node_section.nid)

    # Access coordinates and NIDs from the reader
    coords = node_section.coordinates
    nids = node_section.nid

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

    # delete old deck and any open existant of it and Load existing deck:
    del mesh_deck, node_section

    deck = Deck(Input_File)
    deck.import_file(Input_File)

     # Add new node set to deck:
    node_set_uav = kwd.SetNodeList(sid=2)
    node_set_uav.nodes = target_node_ids_latUAV

     # Check if node sets already exist
    nodesests = list(deck.get_kwds_by_type('SET_NODE_LIST'))
    if nodesests == True:
        print('Node sets already exist in the deck. Check keywoprd notepad.')
    else:
        #Extend deck with new keywords if not
        deck.extend([node_set_uav])
        print('Node sets added successfully.')
        # Create LS-DYNA input deck

        deck_string = deck.write()
        
        del deck

        with open(Input_File, "w") as file_handle:
            file_handle.write(deck_string)

    # Extend deck with new keywords


def setup_nodesets_FoamLat_SegmentSet(Input_File, x_target, y_min, y_max, z_min, z_max, tolerance):
    mesh_deck = mesh.Deck(Input_File)
    node_section = mesh_deck.node_sections[0]
    
    coords = node_section.coordinates
    nids = node_section.nid

    # 1. Identify IDs of nodes on the surface (The "Filter")
    mask = (np.abs(coords[:, 0] - x_target) <= tolerance) & \
           (coords[:, 1] >= y_min) & (coords[:, 1] <= y_max) & \
           (coords[:, 2] >= z_min) & (coords[:, 2] <= z_max)
    
    surface_node_ids = set(nids[mask]) # Using a 'set' for much faster searching
    print(f"Found {len(surface_node_ids)} potential surface nodes.")

    # 2. Extract Element Connectivity
    # Foam is usually SOLID elements (8 nodes)
    solid_section = mesh_deck.element_solid_sections[0] 
    connectivity = np.split(solid_section.node_ids, solid_section.node_id_offsets[1:-1])
    
    segments = []
    
    # Define the 6 local faces of a standard hex element
    # These indices refer to the N1-N8 positions in the connectivity array
    hex_faces = [
        [0, 1, 2, 3], [4, 5, 6, 7], # Bottom / Top
        [0, 1, 5, 4], [1, 2, 6, 5], # Sides
        [2, 3, 7, 6], [3, 0, 4, 7]  # Sides
    ]

    # 3. Find which faces belong to the surface
    for elem in connectivity:
        for face_indices in hex_faces:
            face_nodes = [elem[i] for i in face_indices]
            # If all 4 nodes of this face are in our surface list, it's a segment
            if all(node in surface_node_ids for node in face_nodes):
                segments.append(face_nodes)

    print(f"Identified {len(segments)} surface segments.")

    # 4. Write to Deck
    del mesh_deck, node_section, solid_section # Release file lock
    deck = Deck(Input_File)
    deck.import_file(Input_File)
    
    df_segments = pd.DataFrame(segments, columns=['n1', 'n2', 'n3', 'n4'])
    # SID 100 (or whatever ID you prefer)
    seg_set = kwd.SetSegment(sid=100)
    seg_set.segments = df_segments
    
    deck.extend([seg_set])
    
    deck_string = deck.write()

    del deck
    
    with open(Input_File, "w") as f:
        f.write(deck_string)

#--------------------------------------------------------------------------------------------------------------------------------------
# Configuration for the surface plane for lattice to UAV Body connection
def setup_nodesets_FoamUAV(Input_File, x_max, x_min, z_target, y_min, y_max, tolerance):

    # New Deck using mesh reader to find nodes on surface planes
    mesh_deck = mesh.Deck(Input_File)
    node_section = mesh_deck.node_sections[0]
    print(node_section)

    # Test reading .k file
    print(node_section.coordinates)
    print(node_section.nid)

    # Access coordinates and NIDs from the reader
    coords = node_section.coordinates
    nids = node_section.nid

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

    # delete old deck and any open existant of it and Load existing deck:
    del mesh_deck, node_section

    deck = Deck(Input_File)
    deck.import_file(Input_File)

     # Add new node set to deck:
    node_set_uav = kwd.SetNodeList(sid=3)
    node_set_uav.nodes = target_node_ids_latUAV

     # Check if node sets already exist
    nodesests = list(deck.get_kwds_by_type('SET_NODE_LIST'))
    if nodesests == True:
        print('Node sets already exist in the deck. Check keywoprd notepad.')
    else:
        #Extend deck with new keywords if not
        deck.extend([node_set_uav])
        print('Node sets added successfully.')
        # Create LS-DYNA input deck

        deck_string = deck.write()
        
        del deck

        with open(Input_File, "w") as file_handle:
            file_handle.write(deck_string)

    # Extend deck with new keywords
