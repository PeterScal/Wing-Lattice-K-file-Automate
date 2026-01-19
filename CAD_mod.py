#This changes the lattice to foam thickness ratio

import win32com.client as win32
import pythoncom
import os
import time

def set_lattice_ratio(current_title, dimensionName, new_value_inches, stepfile):
    #Ensure COM is initialized
    pythoncom.CoInitialize()


    #Inputs (Change as needed and .json input in future*****************)
    TARGET_FILE_TITLE = current_title
    #new_value_inches = 3.0  #FLOAT 
    #dimensionName = "D2@Sketch2"
    swModel = None # Model name Initialize to None unitil found

    #SolidWorks Save Status Constant
    SW_SAVE_SUCCESS = 1

    try:
        # 1. Connect to SolidWorks
        swApp = win32.Dispatch("SldWorks.Application")
        print("Connected to SolidWorks.")

        # 2. Get the currently active Part File
        errors = win32.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        
        # This switches focus to the document matching current_title
        swModel = swApp.ActivateDoc3(TARGET_FILE_TITLE, True, 2, errors)

        if swModel is None:
            print("Error: No document is currently active in SolidWorks.")
            raise Exception("No active SolidWorks document found.")
        
        # Check if the active document is the one we want to modify
        full_doc_title = swModel.GetTitle 
        doc_name_only = os.path.splitext(full_doc_title)[0] 
        
        if doc_name_only != TARGET_FILE_TITLE:
            print(f"Error: Active document ('{full_doc_title}') is not the target file ('{TARGET_FILE_TITLE}').")
            raise Exception("Incorrect active document.")

        print(f"Connected to active file: {full_doc_title}")

        #Sets dim name
        swDim = swModel.Parameter(dimensionName)

        #Ensures Correct Dim Name and that it exists
        if swDim:
            #Setting Dimension value
            swDim.Value = new_value_inches
            print(f"Dimension '{dimensionName}' changed using Value property to {swDim.Value} inches.")
            
            #Rebuild model
            rebuild_success = swModel.EditRebuild3
            if rebuild_success != True:
                print("Warning: Model rebuild failed or returned non-success code.")
            print("Model rebuilt.")
            
            #SaveAs to STEP 
            save_result = swModel.SaveAs(stepfile) 
            
            if save_result == SW_SAVE_SUCCESS:
                print("File saved successfully.")
            else:
                # Get the SW error code for more detail
                print(f"Error: File save operation failed. Save2 returned code {save_result}")

        else:
            print(f"Could not find dimension: {dimensionName}")


    except Exception as e:
        print(f"An error occurred: {e}")

print("Script finished.")

