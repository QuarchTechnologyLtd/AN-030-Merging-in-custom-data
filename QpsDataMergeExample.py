"""
AN-030 - Application note demonstrating merging of custom data into a QPS trace

This example is based on our blog: analysing the energy and water consumption of a dishwasher.
This example pulls in custom user data from another source (a water meter in this case) and creates new channels in QPS

It them imports the data into those channels.  Note that the files supplied here will import volume/flow data into
any QPS trace that is at least 29 minutes long.  You can edit the water_rates.csv file or provide your own easily.

To get this data set for water, we captured using a multi-channel PAM, using a digital channel to capture the pulses
from the water meter.  We then used the 'WaterProcessor.py' script, hacked together quickly to process the CSV export
from QPS and turn it into a small number of user data points that we can upload. Custom User Data is intended to
be 'sparse' (ie: perhaps 1 sample per second), adding a lot more can be memory intensive and take some time.

########### VERSION HISTORY ###########

23/04/2024 - Andy Norrie    - First Version
10/12/2024 - Graham Seed    - Use of "$stream import" command to speedup loading CSV data

########### REQUIREMENTS ##############

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

########### INSTRUCTIONS ##############

1- Capture a trace on QPS then 'Save AS'
2- Run the script and follow the instructions on screen.
3- Select your trace when prompted (it must be long enough to take all the user data, 29 minutes for this example)

#######################################
"""

# Import other libraries used in the examples
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Import QPS functions
from quarchpy import qpsInterface, requiredQuarchpyVersion


def main():
    # If required you can enable python logging, quarchpy supports this and your log file
    # will show the process of scanning devices and sending the commands.  Just comment out
    # the line below.  This can be useful to send to quarch if you encounter errors
    # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    print("\n\nQuarch application note example: AN-030")
    print("---------------------------------------\n\n")

    # This is the file containing the user data that we will merge into the trace
    # The .csv file must contain a header of the form:
    # "Time mS","Rate Flow mL/s","Total Volume L", ...
    # That is, a < time, unit > column followed by < channel, group, unit > columns
    merge_filename = "\\EDIT-PATH-FILE\\water_rates.csv"  # eg; "c:\\temp\\csv_files\\water_rates.csv"
    # Version 2.1.24 or higher expected for this application note
    requiredQuarchpyVersion("2.1.24")

    # Ask the user to select the QPS recording to open. This is the one that we will merge the data into
    root = Tk()
    root.withdraw()
    filetypes = (("QPS files", "*.qps"),)
    print("Please open the recording.")
    file_path = askopenfilename(title="Open the recording",filetypes=filetypes)

    # Connect to local QPS
    myQPS = qpsInterface()
    # Open the archived recording
    open_rec = myQPS.open_recording(file_path=file_path)
    print("Open recording response: " + open_rec)

    # Create new channels to for water input, measured in L (for liters) and allowing auto unit scaling (milli/micro)
    use_prefix = 'No'

    # Create the new channels.  These should be unique names.  The 'names' here are Rate and Total.
    # The 'axes' that the data will be added to are the 'flow' and 'volume' and the units for each of the axes is given.
    # You can add multiple unique named channels to an axis group but only if they have the same units of measure.
    print("Adding 2 user channels")
    cmd_result = myQPS.sendCmdVerbose("$create channel " + 'Rate' + " " + 'Flow' + " " + 'mL/s' + " " + use_prefix)
    print("Creation of channel Rate / Flow: " + cmd_result)
    cmd_result = myQPS.sendCmdVerbose("$create channel " + 'Total' + " " + 'Volume' + " " + 'L' + " " + use_prefix)
    print("Creation of channel Total / Volume: " + cmd_result)

    # Our data to merge comes from a water meter, this produces a digital pulse for each unit of water.
    # The data has already been formatted into a rate and total amount channel, to be added to the chart
    # If you want to see how we created this, check out 'WaterProcessor.py'
    print("Adding custom data")
    command = "$stream import file=\"" + merge_filename + "\""
    cmd_result = myQPS.sendCmdVerbose(command)
    print("Importing of CSV values: " + cmd_result)


# Calling the main() function
if __name__ == "__main__":
    main()
