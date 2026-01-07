### Script for Ntop modification

#Import package
import json, os, subprocess
import numpy as np

# Assuming this script, ntop file, and json files will be in the same folder
Current_Directory = os.path.dirname(os.path.abspath(__file__))
exePath = r"C:/Program Files/nTopology/nTopology/nTopCL.exe"  #nTopCL path
nTopFileName = r"WingLattice_v2_CodeTesting.ntop" #nTop notebook file name
nTopFilePath = os.path.join(Current_Directory, nTopFileName)
Input_File_Name = os.path.join(Current_Directory, "input_template.json")
Output_File_Name = os.path.join(Current_Directory, "output_template.json")
Paramter_list_Name = os.path.join(Current_Directory, "Parameter_list.json")

#Index number desiered (change as needed without for loop)
i = 0
#Edit json files:
for i in range(3):

    #Putting thickness value in template by first opening and reading template
    with open(Input_File_Name , "r") as f:
        data = json.load(f)
    
    #Listing current values already in Ntop File
    print('Current Values for parameters: ')
    print("Cell size (mm): ", data["inputs"][0]['value'])
    print("Lattice Thickness (mm): ", data["inputs"][1]['value'])
    print("Unit Cell Rotation (deg): ", data["inputs"][2]['value'])

    with open(Paramter_list_Name, "r") as f1:
        data_1 = json.load(f1)

    #Edit Cell Size Params
    cellsize_x = data_1[0]["Data"][0]["Cell_Size_x"][i]
    cellsize_y = data_1[0]["Data"][0]["Cell_Size_y"][i]
    cellsize_z = data_1[0]["Data"][0]["Cell_Size_z"][i]
    cellsize_array = [cellsize_x, cellsize_y, cellsize_z]
    for item in data["inputs"]:
        if item["name"] == "Cell size": 
            item["value"] = cellsize_array  
    print(cellsize_array)
    

    #Edit beam thickness Params
    Thickness = data_1[2]["Data"][0]["Thickness_Value"][i]
    for item in data["inputs"]:
        if item["name"] == "Lattice thickness": 
            item["value"] = Thickness
    print(Thickness)


    #Edit Rotation Params
    Rotation_x = data_1[1]["Data"][0]["Rotation_x"][i]
    Rotation_y = data_1[1]["Data"][0]["Rotation_y"][i]
    Rotation_z = data_1[1]["Data"][0]["Rotation_z"][i]
    Rotation_array = [Rotation_x, Rotation_y, Rotation_z]
    for item in data["inputs"]:
        if item["name"] == "Rotation": 
            item["value"] = Rotation_array  
    print(Rotation_array)


    #Edit file path
    NewFilePath = data_1[3]["Data"][0]["Lattice_STEP_File_Path"][0]
    for item in data["inputs"]:
        if item["name"] == "Lattice STEP Path": 
            item["value"] = NewFilePath
    print(Thickness)


    #Write all new values to ntop Input file
    with open(Input_File_Name, "w") as f:
        json.dump(data, f, indent=4)


    #nTopCL arguments in a list
    Arguments = [exePath]               #nTopCL path
    Arguments.append("-v2")
    Arguments.append("-j")              #json input argument
    Arguments.append(Input_File_Name)
    Arguments.append("-s")   #json path
    Arguments.append("-o")              #output argument
    Arguments.append(Output_File_Name)  #output json path
    Arguments.append(nTopFilePath)      #.ntop notebook file path

    #Tell user its loading
    print("\nCreating Output...\n")

    #nTopCL call with arguments
    print(" ".join(Arguments))
    process = subprocess.Popen(Arguments)
    process.wait()

 