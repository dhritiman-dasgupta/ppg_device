import tkinter as tk
from tkinter import ttk, font
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from tkinter import filedialog

from collections import deque

def initialize_serial_port(port='COM5', baudrate=115200):
    try:
        ser = serial.Serial(port, baudrate)
        return ser
    except serial.SerialException as e:
        print(f"Error initializing serial port: {e}")
        return None

def close_serial_port(ser):
    if ser:
        ser.close()

def get_available_com_ports():
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    return com_ports

def update_graph(ser, data_buffer, time_buffer, data_buffer_main, time_buffer_main, line, ax, canvas, root):
    try:
        # Read data from the serial port in the format "data,time"
        
        response = ser.readline().decode().strip().split(',')
        
        # Ensure the response list has at least two elements (data and timestamp)
        if len(response) >= 2 and response[0] and response[1]:
            data = float(response[0])
            timestamp = float(response[1])  # Parse timestamp from response
            
            data_buffer.append(data)
            time_buffer.append(timestamp)
            
            data_buffer_main.append(data)
            time_buffer_main.append(timestamp)

            line.set_xdata(time_buffer)
            line.set_ydata(data_buffer)
            
            ax.relim()
            ax.autoscale_view()
            ax.set_xlabel("Time")
            ax.set_ylabel("PPG Value")
            ax.set_title("Real-time Data Acquisition")

            # Redraw the canvas
            canvas.draw()
        else:
            print("Invalid response format:", response)
    except Exception as e:
        print(f"Error: {e}")

    # Call the update_graph function after a certain interval (in milliseconds)
    root.after(1, lambda: update_graph(ser, data_buffer, time_buffer, data_buffer_main, time_buffer_main, line, ax, canvas, root))

def clear_graph(data_buffer, time_buffer, data_buffer_main, time_buffer_main, line, ax, canvas):
    # Clear data buffers
    data_buffer.clear()
    time_buffer.clear()
    data_buffer_main.clear()
    time_buffer_main.clear()

    # Reset plot data
    line.set_xdata([])
    line.set_ydata([])

    # Redraw the canvas
    ax.relim()
    ax.autoscale_view()
    ax.set_xlabel("Time")
    ax.set_ylabel("PPG Value")
    ax.set_title("Real-time Data Acquisition")
    canvas.draw()

def save_to_csv(data_buffer_main, time_buffer_main):
    try:
        # Ask user to choose a file location for saving the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write headers (assuming you want headers)
                csv_writer.writerow(["Time", "PPG Value"])
                # Write data to the CSV file
                for time, data in zip(time_buffer_main, data_buffer_main):
                    csv_writer.writerow([time, data])
            print("Data saved to:", file_path)
        else:
            print("No file selected. Data not saved.")
    except Exception as e:
        print("Error occurred while saving data to CSV:", e)


def on_closing(ser, root):
    close_serial_port(ser)
    root.quit()
    root.destroy()

def main():
    ser = None

    def connect_to_serial():
        nonlocal ser
        selected_port = com_port_combobox.get()
        ser = initialize_serial_port(port=selected_port)
        if ser:
            connect_button.config(state=tk.DISABLED)
            update_graph(ser, data_buffer, time_buffer, data_buffer_main, time_buffer_main, line, ax, canvas, root)

    root = tk.Tk()
    root.title("Data Acquisition")
    root.geometry("1280x720")
    root.configure(bg="white")

    user_font = font.Font(family="Quicksand", size=24, weight="bold")
    prod_label = tk.Label(root, text="DATA ACQUISITION VER-1", font=user_font, fg="blue", bg="white")
    prod_label.pack(pady=10)


    com_label = tk.Label(root, text="Select COM Port:", font=("Quicksand", 16))
    com_label.pack(pady=10)
    available_com_ports = get_available_com_ports()
    com_port_var = tk.StringVar()
    com_port_combobox = ttk.Combobox(root, textvariable=com_port_var, font=("Quicksand", 14))
    com_port_combobox['values'] = available_com_ports
    if available_com_ports:
        com_port_combobox.set(available_com_ports[0])
    com_port_combobox.pack(pady=10)

    # Create the Connect button and pack it to the left side
    connect_button = tk.Button(root, text="Connect", command=connect_to_serial, font=("Quicksand", 10, "bold"), fg="white", bg="green")
    connect_button.place(x=775,y=140)

    #Create the Close button and pack it to the left side
    close_button = tk.Button(root, text="Close", command=lambda: on_closing(ser, root), font=("Quicksand", 10, "bold"), fg="white", bg="red")
    close_button.place(x=845,y=140)

    clear_button = tk.Button(root, text="Clear Graph", command=lambda: clear_graph(data_buffer, time_buffer, data_buffer_main, time_buffer_main, line, ax, canvas), font=("Quicksand", 10, "bold"), fg="white", bg="orange")
    clear_button.place(x=900, y=140)

    clear_button = tk.Button(root, text="Save Graph", command=lambda: save_to_csv(data_buffer_main, time_buffer_main), font=("Quicksand", 10, "bold"), fg="white", bg="orange")
    clear_button.place(x=1000, y=140)

    data_buffer = []
    time_buffer = []
    data_buffer_main = []
    time_buffer_main = []

    fig, ax = plt.subplots(figsize=(15, 15))
    line, = ax.plot([], [], color='blue')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.LEFT, padx=5, pady=20)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(ser, root))
    root.attributes('-toolwindow', 1)
    root.mainloop()

if __name__ == "__main__":
    main()
