import tkinter as tk
from PIL import ImageFont
import os
import utils, constants
import speed
import threading
import queue
import time
import cv2
import numpy as np
from pynput import keyboard
from picamera2 import Picamera2
import simulate_call

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


def image_processing(f):
    blur = f.copy() #cv2.GaussianBlur(frame, (3, 3), 0)

    # Define a kernel
    kernel_size1 = (11, 11)  # Adjust for desired size
    kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size1) #.MORPH_ELLIPSE

    kernel_size2 = (3, 3)  # Adjust for desired size
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size2) #.MORPH_ELLIPSE

    # Perform the opening operation
    opened_image = cv2.morphologyEx(f, cv2.MORPH_OPEN, kernel2)

    # Apply Closing (Dilation followed by Erosion)
    closed_image = cv2.morphologyEx(opened_image, cv2.MORPH_CLOSE, kernel1)
    return closed_image

# Function to approximate and close a contour
def approximate_and_close_contour(contour, epsilon_factor=0.02):
    # Approximate the contour
    epsilon = epsilon_factor * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Check if the contour is closed
    if not np.array_equal(approx[0][0], approx[-1][0]):
        # Add the first point to the end to close the contour
        approx = np.concatenate([approx, approx[:1]], axis=0)
    
    return approx

def bounding_box(f, original, color):
    meta_data_list = []

    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Loop through contours
    for contour in contours:
        closed_contour = approximate_and_close_contour(contour)

        # properties
        x, y, w, h = cv2.boundingRect(closed_contour)
        area = cv2.contourArea(closed_contour)
        
        # TEST and REPLACE WITH ACCURATE RESULTS
        if (area > 80 and area < 400): # nishant runs to nearest traffic light and we test
            # Draw the bounding box
            cv2.rectangle(original, (x, y), (x + w, y + h), (0, 0, 255), 1)
            # cv2.rectangle(f, (x, y), (x + w, y + h), (0, 255, 0), 1)
            
            meta_data_dict = {"pixel_area": area}# "width": w, "height": h, "color": color} # "contour": closed_contour,
            meta_data_list.append(meta_data_dict)
            # print(meta_data_dict, "\n")

    # print(len(meta_data_list), "\n")
    return meta_data_list

"""
        Task that needs to be done:
        - eliminate all smaller contours and contours within a bigger contour ?
            -> Do we actually need it? hopefully can filter inner concentric countours, because complexity increases exponentially

        - Since the contour is closed we can find the area aka the # pixels it bounds
        - fine tune lower and upper thresholds to get our traffic light

        No need:
        - Need to add balck box detection before I try to find traffic lights cuz the assumption is traffic light box is black
            - in morning it can look grayish 


        Define Data Structure:

        bounding box properties =  {"contour"           : closed_contour, 
                                    "pixel area contour": area, 
                                    "width"             : w,
                                    "height"            : h,
                                      }
"""

# Define camera object
# picam2 = Picamera2()
# config = picam2.create_still_configuration(main={"format": 'RGB888', "size": (1920, 1080)})
# picam2.configure(config)
# picam2.start()
# picam2.set_controls({"AfMode": 0 ,"AfTrigger": 0, "AfSpeed": 1, "AfRange": 1})

video_path = "demo.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()


# Display Worker Function
def display_worker():
    global response
    while True:
        # TODO: Integrate with traffic signal detection code
        # if key.char != 'r':
        #     pass
        # else:
        #     return

        # Read a frame from the webcam
        #frame = picam2.capture_array()
        ret, frame = cap.read()
        if not ret:
            break  # Exit if video ends

        cv2.imshow("test input image", frame)
        # continue

        # meta_data_list
        bounding_box_list = []
        red_list = []
        green_list = []
        yellow_list = []

        #final output list for FrontEnd 
        traffic_lights_list = {"straight": [], "left": []}

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Loop through the three color ranges (Red, Green, Yellow)

        ################################################# RED #################################################
        color = "red"
        lower_h = 0
        upper_h = 10
        lower_s = 125#142
        upper_s = 255
        lower_v = 120
        upper_v = 255

        # Define the lower and upper HSV bounds for the current color range
        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        # Create a mask for this color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

        filtered_frame = image_processing(filtered_frame)
        red_list = bounding_box(filtered_frame,frame,color)

        ################################################# GREEN #################################################
        color = "green"
        lower_h = 60
        upper_h = 121
        lower_s = 116
        upper_s = 255
        lower_v = 123
        upper_v = 255

        # Define the lower and upper HSV bounds for the current color range
        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        # Create a mask for this color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

        filtered_frame = image_processing(filtered_frame)
        green_list = bounding_box(filtered_frame,frame,color)

        ################################################# YELLOW #################################################
        color = "yellow"
        lower_h = 11
        upper_h = 56
        lower_s = 146
        upper_s = 255
        lower_v = 147
        upper_v = 255

        # Define the lower and upper HSV bounds for the current color range
        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        # Create a mask for this color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

        filtered_frame = image_processing(filtered_frame)
        yellow_list = bounding_box(filtered_frame,frame,color)
        ##########################################################################################################

        bounding_box_list = red_list + green_list + yellow_list

        #TODO
        # bounding_box_list.sort(key=lambda item: item["contour"][0][0][1], reverse=True)
        bounding_box_list = sorted(bounding_box_list, key=lambda item: item["contour"][0][0][1], reverse=True)

        shape = "NULL"
        for box in bounding_box_list[:2]: 
            contour = box["contour"]
            x, y, width, height = cv2.boundingRect(contour)
            aspect_ratio = width / height  # Compute aspect ratio

            # Check if the shape is a circle
            if 0.9 <= aspect_ratio <= 1.1:  
                shape = "straight"
            else:
                shape = "left"
            
            traffic_lights_list[shape] = box["color"]
        print(traffic_lights_list)

        # ALL PRINTS FOR TEST PURPOSE 

        #print(bounding_box_list)
        # frame = cv2.resize(frame, (640,240))
        # filtered_frame = cv2.resize(filtered_frame, (640,240))
        # cv2.imshow("Webcam", frame)
        cv2.imshow("original", frame)

        # if cv2.waitKey(1) & 0xFF != ord('q'):
        #     break
        print(response)
        # new_response = utils.image_reader()
        new_response = utils.convert_to_display_input(traffic_lights_list)
        print("Checking for new response...")
        if new_response is not None and new_response != response:
            response = new_response
            display_queue.put(response)
        time.sleep(2)
        # time.sleep(0.01)  # Wait for 10 ms before next check

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
    print("Current speed: " ,current_speed)
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

            if current_speed < 0 or current_speed > constants.MAX_SPEED_THRESHOLD:
                continue
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
        picam2.stop() 
        cv2.destroyAllWindows()

root.bind("<Key>", on_key_press)

# Run the Tkinter event loop
root.mainloop()
