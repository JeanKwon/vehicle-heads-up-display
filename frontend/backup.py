import tkinter as tk
from PIL import ImageFont
import os
import utils, constants
import speed
import simulate_call
import threading
import queue
import time

# Initialize the main window
root = tk.Tk()
root.title("HUD Display")

# Set to full window and background to black
root.update_idletasks()
root.configure(bg='black')
root.attributes('-fullscreen', True)
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
signals_frame = tk.Frame(root, bg="black")
signals_frame.pack(fill="both", expand=True)

# Check if the font file exists
if not os.path.exists(constants.FONT_PATH):
    print(f"Font file not found at {constants.FONT_PATH}")
    exit(1)

# Load the custom font
try:
    custom_font = ImageFont.truetype(constants.FONT_PATH, constants.FONT_SIZE)
except Exception as e:
    print(f"Error loading font: {e}")
    exit(1)

# Global variables
response = None
current_speed = None

# Queues for inter-thread communication
display_queue = queue.Queue()
speed_queue = queue.Queue()

# Display Worker Function
def display_worker():
    global response
    while True:
        # TODO: Integrate image reader code
        new_response = simulate_call.generate_response()
        print("Checking for new response...")
        if new_response is not None and new_response != response:
            response = new_response
            display_queue.put(response)
        time.sleep(2)  # Wait for 2 seconds before next check

# Speed Worker Function
def speed_worker():
    global current_speed
    while True:
        new_speed = speed.get_speed()
        if current_speed is None or current_speed != new_speed:
            current_speed = new_speed
            speed_queue.put(current_speed)
        time.sleep(0.1)  # Update every 100 ms

# Display Function to update GUI
def display(response):
    # Clear previous widgets to prevent overlap
    for widget in signals_frame.winfo_children():
        widget.destroy()

    # Check if response exists, else show only speed
    if response is not None and response != 0:
        # 1-digit and not 0: Only left signal
        if response < 10:
            utils.display_left_signal(signals_frame, custom_font, response % 10)
        # If 2-digit: No left signal
        elif response < 100:
            # Only forward
            if response % 10 == 0:
                # Display forward signal
                utils.display_forward_signal(signals_frame, custom_font, response // 10)
            # Forward and right
            else:
                utils.display_forward_signal(signals_frame, custom_font, response // 10)
                utils.display_right_signal(signals_frame, custom_font, response % 10)
        elif 99 < response < 1000:
            utils.display_forward_signal(signals_frame, custom_font, (response % 100) // 10)
            utils.display_left_signal(signals_frame, custom_font, response // 100)
            utils.display_right_signal(signals_frame, custom_font, (response % 100) % 10)

# Update Speed Display Function
def update_speed_display(current_speed):
    utils.display_speed(root, custom_font, current_speed)
    print(f"Current speed: {current_speed}")  # Optional: Print to console

# Poll Queues and Update GUI
def poll_queues():
    try:
        # Process display updates
        while True:
            response = display_queue.get_nowait()
            display(response)
    except queue.Empty:
        pass

    try:
        # Process speed updates
        while True:
            current_speed = speed_queue.get_nowait()
            update_speed_display(current_speed)
    except queue.Empty:
        pass

    # Schedule the next poll
    root.after(50, poll_queues)  # Poll every 50 ms

# Start background threads
display_thread = threading.Thread(target=display_worker, daemon=True)
display_thread.start()

speed_thread = threading.Thread(target=speed_worker, daemon=True)
speed_thread.start()

# Start polling queues
root.after(0, poll_queues)

# Press 'q' to terminate program
def on_key_press(event):
    if event.char.lower() == 'q':
        root.destroy()

root.bind("<Key>", on_key_press)

# Run the Tkinter event loop
root.mainloop()
