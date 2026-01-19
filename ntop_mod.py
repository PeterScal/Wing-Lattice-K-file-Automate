### Script for Ntop modification

#Import package
import json, os, subprocess
import numpy as np

# Assuming this script, ntop file, and json files will be in the same folder
def set_ntop_params(Current_Directory, Input_Template_Name, Output_Template_Name, data, data_1):

    exePath = r"C:/Program Files/nTopology/nTopology/nTopCL.exe"  #nTopCL path
    #nTopFileName = r"WingLattice_v2_CodeTesting.ntop" #nTop notebook file name
    nTopFolderPath = os.path.dirname(Current_Directory)
    nTopFilePath = os.path.join(nTopFolderPath, "nTop", "WingLattice_v2.ntop")  #.ntop notebook file path

    #Index number desiered (change as needed without for loop)

    #Edit json files:

    #Putting thickness value in template by first opening and reading template
        
    #Listing current values already in Ntop File
    print('Current Values for parameters: ')
    print("Cell size (mm): ", data["inputs"][0]['value'])
    print("Lattice Thickness (mm): ", data["inputs"][1]['value'])
    print("Unit Cell Rotation (deg): ", data["inputs"][2]['value'])

    #Edit Cell Size Params
    UVWDIV_x = data_1[0]["Data"][0]["UVW_DIV_x"][0]
    UVWDIV_y = data_1[0]["Data"][0]["UVW_DIV_y"][0]
    UVWDIV_z = data_1[0]["Data"][0]["UVW_DIV_z"][0]
    UVW_array = [UVWDIV_x, UVWDIV_y, UVWDIV_z]
    for item in data["inputs"]:
        if item["name"] == "UVW divisions": 
            item["value"] = UVW_array  
    print(UVW_array)

    #Edit beam thickness Params
    Thickness = data_1[1]["Data"][0]["Thickness_Value"][0]
    for item in data["inputs"]:
        if item["name"] == "Beam thickness": 
            item["value"] = Thickness
    print(Thickness)

    #Edit Lattice file path
    Lattice_NewFilePath = data_1[2]["Data"][0]["Lattice_STEP_File_Path"][0]
    for item in data["inputs"]:
        if item["name"] == "Lattice STEP Path": 
            item["value"] = Lattice_NewFilePath
    print("New Lattice Path Made:")

    #Edit Foam file path
    Foam_NewFilePath = data_1[2]["Data"][0]["Foam_STEP_File_Path"][0]
    for item in data["inputs"]:
        if item["name"] == "Foam STEP Path": 
            item["value"] = Foam_NewFilePath
    print("New Foam Path Made:")

    #Edit Base file path
    Base_NewFilePath = data_1[2]["Data"][0]["Base_STEP_File_Path"][0]
    for item in data["inputs"]:
        if item["name"] == "Base STEP Path": 
            item["value"] = Base_NewFilePath
    print("New Base Path Made:")

    #Write all new values to ntop Input file
    with open(Input_Template_Name, "w") as f:
        json.dump(data, f, indent=4)

    #nTopCL arguments in a list
    Arguments = [exePath]               #nTopCL path
    Arguments.append("-v2")
    Arguments.append("-j")              #json input argument
    Arguments.append(Input_Template_Name)
    Arguments.append("-s")   #json path
    Arguments.append("-o")              #output argument
    Arguments.append(Output_Template_Name)  #output json path
    Arguments.append(nTopFilePath)      #.ntop notebook file path

    #Tell user its loading
    print("\nCreating Output...\n")

    #nTopCL call with arguments
    print(" ".join(Arguments))
    process = subprocess.Popen(Arguments)
    process.wait()

 