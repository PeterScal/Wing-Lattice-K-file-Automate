from ansys.dyna.core import Deck
from ansys.dyna.core import keywords as kwd
import os

# Define file paths
Current_Directory = os.path.dirname(os.path.abspath(__file__))
Input_LatticeFile = os.path.join(Current_Directory, "WingLattice_v2.k")
Output_LatticeFile = os.path.join(Current_Directory, "WingLattice_v2_updated.k")

# Load your existing mesh
deck = Deck(Input_LatticeFile)
deck.import_file(Input_LatticeFile)

# Create the Material keyword (MID 1)
mat = kwd.MatPiecewiseLinearPlasticity(mid=1)
mat.ro = 1.25e-9
mat.e = 1.0
mat.sigy = 0.05
mat.pr = 0.35

# Create the Section keyword (SID 1)
sec = kwd.SectionSolid(secid=1)
sec.elform = 10 # Constant Stress Solid

# Create/Update the Part keyword to link them
part = kwd.Part(pid=1, mid=mat.mid, secid=sec.secid)

# Append these keywords to the deck and write the file
deck.extend([mat, sec, part])

# Create LS-DYNA input deck
deck_string = deck.write()
with open(Input_LatticeFile, "w") as file_handle:
    file_handle.write(deck_string)