################################################################################################################
##                                                                                                            ##
##                          ___  _____ ______   ________  _______   ________                                  ##
##                         |\  \|\   _ \  _   \|\   ___ \|\  ___ \ |\   __  \                                 ##
##                         \ \  \ \  \\\__\ \  \ \  \_|\ \ \   __/|\ \  \|\  \                                ##
##                          \ \  \ \  \\|__| \  \ \  \ \\ \ \  \_|/_\ \   __  \                               ##
##                           \ \  \ \  \    \ \  \ \  \_\\ \ \  \_|\ \ \  \ \  \                              ##
##                            \ \__\ \__\    \ \__\ \_______\ \_______\ \__\ \__\                             ##
##                             \|__|\|__|     \|__|\|_______|\|_______|\|__|\|__|                             ##
##                                                                                                            ##
################################################################################################################                                                                                           
##                                                                                                            ##
##                                                                                                            ##
## This code reads and graphs an Arduino stream of data thought USB                                           ##
##                                                                                                            ##
##  TO DO:                                                                                                    ##
##   - CSV exported data needs to be trasposed                                                                ##
##   - Fix naming of CSV files                                                                                ##
##   - Configure measurement through command line in Python to quicken up further testing                     ##
##                                                                                                            ##
################################################################################################################

#----------------------------------------------------  --------------------------------------------------------#

import serial.tools.list_ports
import serial
import time
import csv
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt



#------------------------------------------------ Functions ----------------------------------------------------#

def read_float_from_serial():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            try:
                value = float(line)
                return value
            except ValueError:
                print("Received invalid float value")

# Function to send a float value
def send_float_through_serial(value):
    value_str = f"{value}\n"
    ser.write(value_str.encode('utf-8'))  # Send the float as a string followed by a newline



#------------------------------- Prompt user to connect and confiugre Arduino ---------------------------------#
print('')
print('/////////////////////////////////////////////////////////////////////')
print('//                                                                 //')
print('//                  Serial Arduino Oscilloscope                    //')
print('//                                                                 //')
print('/////////////////////////////////////////////////////////////////////')
print('\n')

# List all ports available
Ports = serial.tools.list_ports.comports()
Ports_List = []

print('Please connect to the Arduino Serial Port by choosing from the following list:')
for port in Ports:
    Ports_List.append(str(port))
    print(f'  - {str(port)}')

# Request user for port number
port_num = input("Type the arduino Mga port and press enter: COM")
COM = 'COM' + port_num

# Open COM and wait up to 2 seconds for communication
try:
    ser = serial.Serial(COM, baudrate=9600, timeout=2)
    print("\nSuccesfuly connected to oscilloscope!")

except Exception as e:
    print(f"\nAn error ocurred when attempting to connect to "+COM+": {e}")

print('')
print('/////////////////////////////////////////////////////////////////////')
print('')

# Read default configuration variables for measurement
Trigger_threshold_V = read_float_from_serial()
ADC_voltage_ref = read_float_from_serial()
number_samples = int( read_float_from_serial() )
Nyquist_frequency = read_float_from_serial()

print('Please configure measurement. Default configuration variables are:\n')
print(f'  - Trigger threshold = {Trigger_threshold_V}V\n')
print(f"  - ADC voltage reference = {ADC_voltage_ref}\n")
print(f"  - Number samples = {number_samples}\n")
print(f"  - Maximum measurable frequency = {Nyquist_frequency}\n")


# Ask user if they want to configure the oscilloscope measurement
Reconfigure = input("Would you like to configure the measurement? [y] or [n]: ")
if (Reconfigure == 'y' or Reconfigure == 'yes' or Reconfigure == '[y]' or Reconfigure == 'Y'):

    # Signal Arduino to store the following values
    Reconfigure = 'y'
    ser.write(Reconfigure.encode('utf-8'))

    send_float_through_serial( float( input("  - Enter trigger threshold in volts: ") ) )
    send_float_through_serial( float( input("  - Enter ADC reference voltage in volts: ") ) ) 
    send_float_through_serial( float( input("  - Enter number of samples: ") ) )
    send_float_through_serial( float( input("  - Enter maximum frequency to measure in Hz: ") ) )

else:
    # Signal Arduino to measure with it's default values
    Reconfigure = 'n'
    ser.write(Reconfigure.encode('utf-8'))

print('')
print('/////////////////////////////////////////////////////////////////////')
print('')




#----------------------------------------------- Read data ----------------------------------------------------#
print('Begin measurement')
# Read data from arduino
Captured_data = [[], []]
Store_data = False
while True:

    try:
        # Wait until response or timeout
        wait = 0
        timeout = 10
        while((ser.in_waiting == 0) and (wait < timeout)):
            time.sleep(1)
            wait = wait + 1
        wait = 0

        # Read response, it may come in 2 different formats
        try:
            # Message format
            arduinoData = ser.readline().decode('ascii')
        except:
            # Data format
            arduinoData = ser.readline().decode('utf-8').strip()

        print(arduinoData)

        # End communication when requested by Arduino
        if ('Close Communication' in arduinoData):
            Store_data = False
            break

        if (Store_data):

            # Parse CSV data
            reader = csv.reader([arduinoData])
            for row in reader:
                Captured_data[0].append(float(row[0]))
                Captured_data[1].append(float(row[1]))

        # Log data when prompted by Arduino
        if ('Sending captured data' in arduinoData):            
            Store_data = True


    except Exception as e:
        print(f"An error ocurred when reading: {e}")
        break
    

# Close serial comms
if ser.is_open:
    try:
        ser.close()
        time.sleep(1)  # Give the OS some time to release the port
        print(f"Closed "+COM+" succesfuly")

    except Exception as e:
        print(f"An error ocurred when clossing "+COM+" {e}")



#------------------------------------------ Graph and store data -----------------------------------------------#

print('')
print('/////////////////////////////////////////////////////////////////////')
print('')

# Graph data
fig, ax = plt.subplots()
plt.plot(Captured_data[0], Captured_data[1], color='k')#, label="")
plt.xticks(Captured_data[0])
plt.xlabel('Time [ms]')
plt.ylabel('Voltage [V]')
plt.legend()
plt.show()



# Export data to CSV
Export_Data = input('Export data to CSV? [y] or [n]: ')
if(Export_Data == 'y' or Export_Data == 'Y' or Export_Data == 'yes'):
    
    # Construct column names
    headers = ['Time [ms]', ['Voltage [V]']]

    # Write to CSV dynamicaly
    
    # Define the folder and file path
    folder_name = 'Data_logs'

    # Differentiate files by time of creation
    now = datetime.datetime.now()
    now_trimmed = now.strftime("%Y%m%d_%H%M%S")
    file_name = 'Log_' + str(now_trimmed) + '.csv'
    file_path = os.path.join(folder_name, file_name)

    # Create the subfolder if it does not exist
    os.makedirs(folder_name, exist_ok=True)

    # Write data to CSV
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time [ms]', 'Voltage [V]'])  # Write header
        writer.writerows(Captured_data)

    print(f"Data successfully written to {file_path}")
