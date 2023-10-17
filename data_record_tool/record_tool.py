import serial
import serial.tools.list_ports
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def print_available_serial_ports():
    available_ports = serial.tools.list_ports.comports()
    if available_ports:
        print("Available Serial Ports:")
        for port, desc, hwid in sorted(available_ports):
            print(f"- {port}: {desc} [{hwid}]")
    else:
        print("No serial ports available.")

print("Available Serial Ports -->")
print_available_serial_ports()

print("Enter the Serial Port -->")
serialport = str(input()).upper()

print("Get the time in sec -->")
t = int(input())

try:
    ser = serial.Serial(serialport, 115200)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'acquisition_data_{current_time}.csv'
    plot_filename = f'ppg_plot_{current_time}.png'
    
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['PPG', 'TIME'])
        
        start_time = time.time()
        end_time = start_time + t  # Capture data for 1 minute
        
        ppg_data = []
        time_data = []
        
        while time.time() < end_time:
            # Read data from Arduino
            data = ser.readline().decode().strip()  # Read and decode the data
            
            try:
                ppg, timestamp = map(float, data.split(','))
                csv_writer.writerow([ppg, timestamp])
                ppg_data.append(ppg)
                time_data.append(timestamp)
            except ValueError:
                print("Invalid data format:", data)
            
            # Print the received data (optional)
            print("Received data:", data)

        # Create a DataFrame from the collected data
        data_frame = pd.DataFrame({'PPG': ppg_data, 'TIME': time_data})
        
        # Define the path where the CSV file will be saved
        current_directory = os.getcwd()
        csv_file_path = os.path.join(current_directory, filename)

        print("CSV file saved at:", csv_file_path)

        # Save the DataFrame to CSV file
        data_frame.to_csv(csv_file_path, index=False)

        # Plotting the data
        plt.figure(figsize=(10, 6))
        plt.plot(data_frame['TIME'], data_frame['PPG'], marker='.', linestyle=':')
        plt.xlabel('Time')
        plt.ylabel('PPG')
        plt.title('PPG vs. Time')
        plt.grid(True)

        # Save the plot as an image
        plot_file_path = os.path.join(current_directory, plot_filename)
        plt.savefig(plot_file_path)

        print("Graph saved at:", plot_file_path)

        # Display the plot
        plt.show()

except serial.SerialException as e:
    print(f"Please check the specified serial port.")
except KeyboardInterrupt:
    print("Exiting the program")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
