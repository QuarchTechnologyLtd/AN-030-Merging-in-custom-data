"""
AN-029 - Application note demonstrating merging of custom data into a QPS trace

This example demonstrates adding annotations and datapoints to a QPS stream.

########### VERSION HISTORY ###########

19/04/2024 - Andy Norrie    - First Version.

########### REQUIREMENTS ###########

1- Python (3.x recommended)
    https://www.python.org/downloads/
2- Quarchpy python package
    https://quarch.com/products/quarchpy-python-package/
3- Quarch USB driver (Required for USB connected devices on Windows only)
    https://quarch.com/downloads/driver/
4- Check USB permissions if using Linux:
    https://quarch.com/support/faqs/usb/
5- Java 8, with JaxaFX
    https://quarch.com/support/faqs/java/

########### INSTRUCTIONS ###########

1- Connect a Quarch module to your PC via USB, Serial or LAN and power it on.
2- Run the script and follow the instructions on screen.

####################################
"""

# Import other libraries used in the examples
import os
import time
from quarchpy.user_interface import printText, visual_sleep
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

# Import QPS functions
from quarchpy import qpsInterface, isQpsRunning, startLocalQps, GetQpsModuleSelection, getQuarchDevice, quarchDevice, quarchQPS, \
    requiredQuarchpyVersion


def main():
    # If required you can enable python logging, quarchpy supports this and your log file
    # will show the process of scanning devices and sending the commands.  Just comment out
    # the line below.  This can be useful to send to quarch if you encounter errors
    # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

    print("\n\nQuarch application note example: AN-029")
    print("---------------------------------------\n\n")

    # Version 2.0.15 or higher expected for this application note
    requiredQuarchpyVersion("2.0.15")

    # File paths for the example are set here, and can be altered to put your data files in a different location
    # The path must be writable via a standard OS path
    filePath = os.path.dirname(os.path.realpath(__file__))

    # Ask the user to select the QPS recording to open. This is the one that we will merge the data into
    root = Tk()
    root.withdraw()
    filetypes = (("QPS files", "*.qps"))
    print("Please open the recording.")
    file_path = askopenfilename(title="Open the recording")
    #fp_arg = "-open=" + '"' + file_path + '"'
    #startLocalQps(args=[fp_arg])
    
    # Connect to local QPS
    myQPS = qpsInterface()
    print(myQPS.sendCmdVerbose("$open recording qpsFile=\""+str(file_path)+"\""))

    # Wait for the trace to load: TODO: replace with poll for QPS ready
    visual_sleep(60,1, "Waiting for QPS to fully load the trace")

    

    # Create new channels to for water input, measured in L (for liters) and allowing auto unti scaling (milli/micro)
    myNewGroup = 'Water'
    myRateChannel = 'Rate'
    myTotalChannel = 'Total'
    myBaseUnits = 'L'
    usePrefix = 'yes'
    timeFormat = 'elapsed'
    
    # Create the new channels
    myQPS.sendCmdVerbose("$create channel " + myRateChannel + " " + myNewGroup + " " + myBaseUnits + " " + usePrefix)
    myQPS.sendCmdVerbose("$create channel " + myTotalChannel + " " + myNewGroup + " " + myBaseUnits + " " + usePrefix)
    
    # Our data to merge comes from a water meter, this produces a digital pulse for each unit of water.
    # The data has already been formatted into a rate and total amount channel, to be added to the chart
    line_num = 0
    with open(filename, 'r') as file:
        for line in file:
        
            # Skip header row
            if (line_num == 0):
                line_num=line_num+1                
                continue    
        
            # Split into sections
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue  # Skip lines that don't have at least two columns          
                
            timeStr = parts[0] + 'ms'
            valueStr = parts[1]
            myQPS.sendCmdVerbose("$stream data add " + myRateChannel + " " + myNewGroup + " " + timeStr + " " + valueStr + " " + timeFormat)
            valueStr = parts[2]
            myQPS.sendCmdVerbose("$stream data add " + myTotalChannel + " " + myNewGroup + " " + timeStr + " " + valueStr + " " + timeFormat)
    
    


# Calling the main() function
if __name__=="__main__":
    main()