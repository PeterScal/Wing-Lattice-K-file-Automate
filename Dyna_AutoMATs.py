from ansys.dyna.core import Deck
from ansys.dyna.core import keywords as kwd
import os
import numpy as np

# Define file paths
Current_Directory = os.path.dirname(os.path.abspath(__file__))
Ls_Dyna_Folder = os.path.dirname(Current_Directory)

# Path to the file containing the NODE definitions
Input_LatticeFile = os.path.join(Ls_Dyna_Folder,"LS-DYNA", "WingLattice_v2.k") 

# Load your existing mesh
deck = Deck(Input_LatticeFile)
deck.import_file(Input_LatticeFile)

# Create the Material keyword (MID 1)
mat = kwd.MatPiecewiseLinearPlasticity(mid=1)
mat.ro = 1.25e-9
mat.e = 1.0
mat.sigy = 0.05
mat.pr = 0.35
mat.etan = 0.2

# Create the Section keyword (SECID 3)
sec = kwd.SectionSolid(secid=3)
sec.elform = 10 # Constant Stress Solid

# Create the Part keyword (PID 1) linking to the Material and Section   
part = kwd.Part(pid=1, mid=mat.mid, secid=sec.secid)

#--------------------------------------------------------------------------------------------------------------------------------------
if deck.get_kwds_by_type('MATERIAL') is not None and deck.get_kwds_by_type('SECTION') is not None:
    print('Material or Section already exist in the deck. Check keywoprd notepad.')
    SystemExit
else:
    deck.extend([mat, sec, part])

# Create LS-DYNA input deck
deck_string = deck.write()
with open(Input_LatticeFile, "w") as file_handle:
    file_handle.write(deck_string)