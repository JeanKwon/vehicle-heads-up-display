import cv2
import numpy as np
from pynput import keyboard
from picamera2 import Picamera2


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
def approximate_and_close_contour(contour, epsilon_factor=0.001):
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
        if (area > 0):# and area < 400): # nishant runs to nearest traffic light and we test
            # Draw the bounding box
            cv2.rectangle(original, (x, y), (x + w, y + h), (0, 255, 0), 1)
            # cv2.rectangle(f, (x, y), (x + w, y + h), (0, 255, 0), 1)
            
            meta_data_dict = {"pixel_area": area}# "width": w, "height": h, "color": color} # "contour": closed_contour,
            meta_data_list.append(meta_data_dict)

            # f = cv2.resize(frame, (840,640))
            # cv2.imshow(str(color), f)
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
video_path = "traffic_light_2.h264"
cap = cv2.VideoCapture(video_path)


if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

while True:

    # if key.char != 'r':
    #     pass
    # else:
    #     return

    # Read a frame from the webcam
    # frame = picam2.capture_array()

    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
            
    # meta_data_list
    bounding_box_list = []
    red_list = []
    green_list = []
    yellow_list = []

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Loop through the three color ranges (Red, Green, Yellow)

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

    bounding_box_list = red_list + green_list + yellow_list

    # ALL PRINTS FOR TEST PURPOSE 

    # print(bounding_box_list)
    # print()
    # frame = cv2.resize(frame, (840,640))
    # filtered_frame = cv2.resize(filtered_frame, (640,240))
    # cv2.imshow("Webcam", frame)
    cv2.imshow("original", frame)

    # cv2.waitKey(0)

    # Exit loop if 'q' is pressed
    
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break
    
    # if cv2.waitKey(1) & 0xFF != ord('q'):
    #     break

# Setup the listener for key presses
# with keyboard.Listener(on_press=on_press) as listener:
#     listener.join()

# When everything is done, release the capture and close windows
cap.release() 
#picam2.stop() 
cv2.destroyAllWindows()


""" 
Red Light
H: 0-10
S: 142-255
V: 120-255

Yellow Light
H: 11-56
S: 146-255
V: 147-255

Green Light
H: 60-121
S: 116-255
V: 123-255

"""
