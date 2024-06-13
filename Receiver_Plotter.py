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



#------------------------------------ Prompt user to connect to Arduino ---------------------------------------#

# List all ports available
Ports = serial.tools.list_ports.comports()
Ports_List = []

for port in Ports:
    Ports_List.append(str(port))
    print(str(port))

# Request user for port number
port_num = input("Select Arduino MEGA Port: COM")
COM = 'COM' + port_num

# Open COM and wait up to 2 seconds for communication
try:
    ser = serial.Serial(COM, baudrate=9600, timeout=2)

except Exception as e:
    print(f"An error ocurred when attempting to connect to "+COM+": {e}")



#----------------------------------------------- Read data ----------------------------------------------------#

# Read data from arduino
Captured_data = [[], []]
Store_data = False
while True:

    try:
        # Request data from arduino
        #ser.write(b's')

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
