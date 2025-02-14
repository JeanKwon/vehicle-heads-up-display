import time
import os
import re
from pynput import keyboard
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

# Function to find the next count based on existing video files
def get_next_count():
    # Get a list of files in the current directory
    files = os.listdir(".")
    
    # Regular expression to match the traffic_light_<number>.h264 pattern
    pattern = re.compile(r"traffic_light_(\d+)\.h264")
    
    max_count = 0  # Default to 0 if no files found
    
    # Iterate over files and extract the integer values
    for file in files:
        match = pattern.match(file)
        if match:
            # Extract the integer value from the filename
            count_value = int(match.group(1))
            # Update max_count if we find a larger value
            max_count = max(max_count, count_value)
    
    # Return the next count (one greater than the largest found value)
    return max_count + 1

# Initialize the camera and encoder
picam2 = Picamera2()

video_config = picam2.create_video_configuration(main={"size": (1920, 1080)})
picam2.configure(video_config)

encoder = H264Encoder(10000000)

recording = False
count = get_next_count()  # Get the next available count based on existing files
start_time = None  # To track when the recording started

def on_press(key):
    global recording, start_time, count

    try:
        if key.char == 'r' and not recording:
            # Start recording when 'r' is pressed and recording hasn't started yet
            filename = f"traffic_light_{count}.h264"
            print(f"Recording started... Saving to {filename}")
            picam2.start_recording(encoder, filename)
            recording = True
            start_time = time.time()  # Record the start time when recording begins

        elif key.char == 's' and recording:
            # Stop recording when 's' is pressed and recording is active
            print("Recording stopped...")
            picam2.stop_recording()
            recording = False
            count += 1  # Increment the counter to prepare for the next video

        elif key.char == 'q':
            # Stop the listener and terminate the program when 'q' is pressed
            print("Exiting the program...")
            return False  # This stops the listener and exits the program

    except AttributeError:
        # Handle special keys like "esc"
        pass

    # Automatically stop recording after 3 minutes (180 seconds)
    if recording and time.time() - start_time >= 180:
        print("Recording time exceeded 3 minutes, stopping automatically...")
        picam2.stop_recording()
        recording = False
        count += 1  # Increment the counter to prepare for the next video

# Setup the listener for key presses
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
