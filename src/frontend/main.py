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
    kernel = np.array([[-1, -1, -1],
                   [-1, 9, -1],
                   [-1, -1, -1]])
    
    # Define a kernel
    kernel_size1 = (7, 7)  # Adjust for desired size
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size1) #.MORPH_ELLIPSE

    kernel_size2 = (3, 3)  # Adjust for desired size
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size2) #.MORPH_ELLIPSE
    


    sharp = cv2.filter2D(f, -1, kernel)
    blur = cv2.GaussianBlur(sharp, (5, 5), 0)
    
    opened_image = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel2)

    closed_image = cv2.morphologyEx(blur, cv2.MORPH_CLOSE, kernel1) 

    return closed_image

# Function to approximate and close a contour
def approximate_and_close_contour(contour, epsilon_factor=0.02):
    epsilon = epsilon_factor * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if not np.array_equal(approx[0][0], approx[-1][0]):
        approx = np.concatenate([approx, approx[:1]], axis=0)
    return approx

def bounding_box(f, original, color):
    meta_data_list = []

    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        closed_contour = approximate_and_close_contour(contour)
        x, y, w, h = cv2.boundingRect(closed_contour)
        area = cv2.contourArea(closed_contour)
        
        # TEST and REPLACE WITH ACCURATE RESULTS
        if 80 < area < 400:
            # Draw the bounding box
            cv2.rectangle(original, (x, y), (x + w, y + h), (0, 0, 255), 1)
            
            # Uncomment color/contour so your later code works
            meta_data_dict = {
                "pixel_area": area,
                "contour": closed_contour,
                "color": color
            }
            meta_data_list.append(meta_data_dict)

    return meta_data_list

# (If you want to use the PiCamera, uncomment and configure)
# picam2 = Picamera2()
# config = picam2.create_still_configuration(main={"format": 'RGB888', "size": (1920, 1080)})
# picam2.configure(config)
# picam2.start()
# picam2.set_controls({"AfMode": 0 ,"AfTrigger": 0, "AfSpeed": 1, "AfRange": 1})

video_path = "traffic_light_2.h264"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Display Worker Function
def display_worker():
    global response
    while True:
        # Read a frame from cap (or from picam2 if used)
        ret, frame = cap.read()
        if not ret:
            break  # Exit if video ends

        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        ################################################# RED #################################################
        color = "red"
        lower_h = 0
        upper_h = 5
        lower_s = 150
        upper_s = 255
        lower_v = 150
        upper_v = 255

        h_r_low = 175
        h_r_high = 179

        # Define the lower and upper HSV bounds for the two red hue ranges
        lower_bound1 = np.array([lower_h, lower_s, lower_v])
        upper_bound1 = np.array([upper_h, upper_s, upper_v])

        lower_bound2 = np.array([h_r_low, lower_s, lower_v])
        upper_bound2 = np.array([h_r_high, upper_s, upper_v])

        # Create masks for both red hue ranges
        mask1 = cv2.inRange(hsv, lower_bound1, upper_bound1)
        mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)

        # Combine the two masks
        mask = cv2.bitwise_or(mask1, mask2)

        filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

        filtered_frame = image_processing(filtered_frame)
        red_list = bounding_box(filtered_frame,frame,color)

        ################################################# GREEN #################################################
        color = "green"
        lower_h = 60
        upper_h = 94
        lower_s = 50
        upper_s = 255
        lower_v = 142
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
        '''
        color = "yellow"
        lower_h = 7
        upper_h = 28
        lower_s = 58
        upper_s = 255
        lower_v = 232
        upper_v = 255

        # Define the lower and upper HSV bounds for the current color range
        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        # Create a mask for this color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

        filtered_frame = image_processing(filtered_frame)
        yellow_list = bounding_box(filtered_frame,frame,color)
        '''
        ##########################################################################################################

        bounding_box_list = red_list + green_list #+ yellow_list

        # Sort bounding boxes if needed
        bounding_box_list = sorted(
            bounding_box_list,
            key=lambda item: item["contour"][0][0][1],
            reverse=True
        )

        # Build final output list for FrontEnd
        traffic_lights_list = {"straight": [], "left": []}
        shape = "NULL"
        for box in bounding_box_list[:2]:
            contour = box["contour"]
            x, y, width, height = cv2.boundingRect(contour)
            aspect_ratio = width / height if height else 0
            if 0.9 <= aspect_ratio <= 1.1:
                shape = "straight"
            else:
                shape = "left"
            traffic_lights_list[shape] = box["color"]

        # Show the bounding-box-annotated frame in one window
        cv2.imshow("original", frame)
        cv2.waitKey(1)  # **REQUIRED** so OpenCV can refresh its window

        # Convert that traffic_lights_list to your "response"
        print(traffic_lights_list)
        new_response = utils.convert_to_display_input(traffic_lights_list)
        if new_response is not None and new_response != response:
            response = new_response
            display_queue.put(response)

        print("Checking for new response...")
        print("Current response:", response)

        time.sleep(0.1)

# Speed Worker Function
def speed_worker():
    global current_speed
    while True:
        new_speed = speed.get_speed()
        print("New speed: ", new_speed)
        if current_speed is None or current_speed != new_speed:
            current_speed = new_speed
            speed_queue.put(current_speed)
        time.sleep(0.01)

# Display Function to update GUI
def display(response):
    # Clear previous widgets
    for widget in signals_frame.winfo_children():
        widget.destroy()

    # Check if response exists
    if response is not None and response != 0:
        # 1-digit and not 0: Only left signal
        if response < 10:
            utils.display_left_signal(signals_frame, custom_font, response % 10)
        # 2-digit => forward + maybe right
        elif response < 100:
            if response % 10 == 0:
                utils.display_forward_signal(signals_frame, custom_font, response // 10)
            else:
                utils.display_forward_signal(signals_frame, custom_font, response // 10)
                utils.display_right_signal(signals_frame, custom_font, response % 10)
        elif 99 < response < 1000:
            utils.display_forward_signal(signals_frame, custom_font, (response % 100) // 10)
            utils.display_left_signal(signals_frame, custom_font, response // 100)
            utils.display_right_signal(signals_frame, custom_font, (response % 100) % 10)

# Update Speed Display Function
def update_speed_display(current_speed):
    print("Current speed:", current_speed)
    utils.display_speed(root, custom_font, current_speed)
    print(f"Current speed: {current_speed}")

def poll_queues():
    try:
        while True:
            resp = display_queue.get_nowait()
            display(resp)
    except queue.Empty:
        pass

    try:
        while True:
            spd = speed_queue.get_nowait()
            if spd < 0 or spd > constants.MAX_SPEED_THRESHOLD:
                continue
            update_speed_display(spd)
    except queue.Empty:
        pass

    root.after(50, poll_queues)

# Start threads
display_thread = threading.Thread(target=display_worker, daemon=True)
display_thread.start()

speed_thread = threading.Thread(target=speed_worker, daemon=True)
speed_thread.start()

root.after(0, poll_queues)

def on_key_press(event):
    if event.char.lower() == 'q':
        root.destroy()
        picam2.stop() 
        cv2.destroyAllWindows()

root.bind("<Key>", on_key_press)

root.mainloop()
