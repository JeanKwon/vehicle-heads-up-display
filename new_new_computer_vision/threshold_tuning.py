import cv2
import numpy as np

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
        if (area < 400) and (area > 50): # nishant runs to nearest traffic light and we test
            # Draw the bounding box
            cv2.rectangle(original, (x, y), (x + w, y + h), (0, 255, 0), 1)
            # cv2.rectangle(f, (x, y), (x + w, y + h), (0, 255, 0), 1)
            
            meta_data_dict = {"contour": closed_contour, "pixel_area": area, "width": w, "height": h, "color": color}
            meta_data_list.append(meta_data_dict)
            # print(meta_data_dict, "\n")

    print(len(meta_data_list), "\n")
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

        
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

while True:
    # Read a frame from the webcam
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
    upper_h = 10
    lower_s = 142
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

    # ALL PRINTS FOR TEST PURPOSE 

    # print(bounding_box_list)
    # frame = cv2.resize(frame, (640,240))
    # filtered_frame = cv2.resize(filtered_frame, (640,240))
    # cv2.imshow("Webcam", frame)
    cv2.imshow("original", frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and close windows
cap.release()
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
