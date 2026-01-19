import os
import subprocess


def run_Ls_Dyna(input_dir, input_file):
    # --- 1. SET UP THE PATHS ---
    # This script is in D:\Modified_Wing\Scripts
    



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