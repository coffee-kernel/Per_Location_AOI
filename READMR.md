# **** Per location AOI Project (Beta Test) **** #

# **** Description **** #
-> Testing of Mainboards Labels, mylars, foam, gasket etc.
-> it detects if the location of label from MB is missing, misaligned or wrong in position
-> Need to train manually the GOOD sample mainboard and also the NG mainboard for better result
-> This is beta test so its free for adjustments especially to confidence threshold and logic

# **** Things to have **** #
-> DSLR Camera
-> Secondary Webcam for live feed
-> Laptop with GPU (Desktop With GPU)

# **** Main UI Walkthrough **** #
-> Start the UI
-> Choose where profiling process/NG
-> Serial number entry - Scan a serial or input directly
-> MB Position - TOP VIEW and BOTTOM VIEW
-> Capture button - Automatically captures the MB using gphoto2
-> Inspect button - Trigger the main logic here match the ROI image all over the captured image on a specific time
-> Save button - Save the trained ROI image and its annotations data via JSON file
-> Re-Inspect button - Clears the results and start new video feed on screen
-> Refresh button - Used for profiling to clear the canvas
-> Delete button - Used for deleting the dropdown data and the serial number entry

# **** Process Profiling **** #
-> Capture the MB
-> Start to draw or annotate on that MB
-> Click save button

# **** Inspection process **** #
-> Capture the MB UUI
-> Click the inspect button
-> Wait for messagebox for the results
-> Display automatically the result image save all the data needed

# **** Steps to access files ****
1. Clone the repository
2. Install packages from requirements.txt


