import os
import subprocess

# --- 1. SET UP THE PATHS ---
# This script is in D:\Modified_Wing\Scripts
current_dir = os.path.dirname(os.path.abspath(__file__))

# Move up one level to D:\Modified_Wing
parent_dir = os.path.dirname(current_dir)

# Go into the LS-DYNA folder to find the .k file
input_dir = os.path.join(parent_dir, "LS-DYNA")
input_file = os.path.join(input_dir, "WingLattice_v2.k")

# Path to your specific Student R16.1 solver
solver_exe = r"C:\Program Files\LS-DYNA Suite R16.1 Student\lsdyna\ls-dyna_smp_d_R16.1_180-gd50332dbe5_winx64_ifort190_sse2_studentversion.exe"

# --- 2. BUILD THE COMMAND ---
# 'i=' is input, 'ncpu' is cores, 'memory' is RAM
dyna_command = [
    f'"{solver_exe}"', 
    f'i="{input_file}"', 
    'ncpu=4', 
    'memory=200m'
]

# Combine the list into one single string for the shell
full_command_string = " ".join(dyna_command)

# --- 3. RUN THE SIMULATION ---
print(f"Executing: {full_command_string}")
print(f"Working Directory: {input_dir}")

try:
    # cwd=input_dir is critical: it tells LS-DYNA to save results 
    # (d3plots, messag, etc.) in the folder with the .k file.
    subprocess.run(full_command_string, cwd=input_dir, shell=True)
    
    print("\n--- Process Finished ---")

except Exception as e:
    print(f"An error occurred: {e}")