import math
    
    
# This iterates through an input CSV (exported from a QPS digital channel in our case).
# For ease of writing, we work in a couple of steps
# First we turn the PWM style capture into a more simple format, where column 1 is an event flag, showing a pulse (rising edge) ocurred
# We output a compressed version of the CSV which only contains the timestamped lines where a pulse ocurred.  This is much smaller to process
# We then process this reduced data, producing a rate and total channel which can be uploaded
def process_reduced_data (filename, outname):
    
    line_num=0
    last_time=0
    zero_threshold_ms = 1000
    calFactor = 0.000847 # (liters per pulse)
    rate = 0
    total = 0
    
    outfile = open (outname, 'w')
    with open(filename, 'r') as file:
        for line in file:
            # Skip header row
            if (line_num == 0):
                line_num=line_num+1
                outfile.write("Time mS,Rate,Total\n")
                continue                    
            
            # Split into sections
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue  # Skip lines that don't have at least two columns                               
                
            # Make sure there is always a time 0 point in the output
            if (line_num == 1):
                line_num=line_num+1
                if (parts[0] != 0):
                    outfile.write("0,0,0\n")
            
            # Check when the last pulse happened in mS
            line_time = int(parts[0])
            delta_time = (line_time - last_time) / 1000000
            
            # Sum the pulses
            total = total + 1
            
            # If the last one was more than the threshold ago, the rate is 0
            if (delta_time > zero_threshold_ms):
                rate = 0;
            else:
                # Convert to mS for calculations
                rate = 1000 / delta_time
                
            # For zero rates, we need to write points on both sides of the zero region, to make sure we draw the rate line correctly
            if (rate == 0):
                outfile.write (str((math.floor(last_time / 1000000))+1) + "," + str(rate * calFactor) + "," + str(total * calFactor) + "\n")
                outfile.write(str((math.floor(line_time / 1000000))-1) + "," + str(rate * calFactor) + "," + str(total * calFactor) + "\n")
            else:
                outfile.write (str(math.floor(line_time / 1000000)) + "," + str(rate * calFactor) + "," + str(total * calFactor) + "\n")

            # Track the last time point
            last_time = line_time
        # Insert a zero row at the end if there is not one already, to close off the data
        if (rate != 0):
            outfile.write (str((line_time + 1000) / 1000000) + ',0,' + str(total * calFactor))
                                            

# Takes a CSV format export from QPS, with a digital channel in column 1 that needs processed to find
# Each rising edge, indicating a pulse from the water meter.  This simplifies the next steps, as we
# only worry about points with an obvious value.  The output is a CSV with a '1' for a single pulse
def locate_transitions(filename, outname, allRows=False):
    linenum=0
    outfile = open (outname, 'w')
    with open(filename, 'r') as file:
        last_flag = None
        transition_count = 0
        for line in file:
            if (linenum==0):
                linenum=linenum+1
                outfile.write(line)
                continue
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue  # Skip lines that don't have at least two columns
            current_flag = int(parts[1])
            if last_flag is not None and last_flag != current_flag:
                if (current_flag == 1):
                    transition_count += 1
                    outfile.write(line)
                elif (allRows):
                    parts[1] = "0"
                    outfile.write(",".join(parts) + '\n')
            elif (allRows):
                parts[1] = "0"
                outfile.write(",".join(parts) + "\n")
            last_flag = current_flag
        outfile.close ()
        return transition_count

filename = 'FileExportedFromQps.csv'
print ("Processing raw data file: " + filename)
total_transitions = locate_transitions(filename, 'pulses.csv', False)
print(f'Total pulses found: {total_transitions}')
process_reduced_data ('pulses.csv', 'output_rates.csv')
print ('Data reduced to timestamped events')