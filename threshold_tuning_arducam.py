import cv2
import numpy as np
from picamera2 import Picamera2





def nothing(x):
    pass

def image_processing(f):
    blur = f #cv2.GaussianBlur(frame, (3, 3), 0)

    # Define a kernel
    kernel_size1 = (11, 11)  # Adjust for desired size
    kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size1) #.MORPH_ELLIPSE

    kernel_size2 = (3, 3)  # Adjust for desired size
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size2) #.MORPH_ELLIPSE

    # Perform the opening operation
    opened_image = cv2.morphologyEx(f, cv2.MORPH_OPEN, kernel2)
    # return opened_image

    # Apply Closing (Dilation followed by Erosion)
    closed_image = cv2.morphologyEx(opened_image, cv2.MORPH_CLOSE, kernel1)
    return closed_image

# Function to check if a contour is closed
def is_contour_closed(contour):
    # Check if the contour is convex (a strong indication of a closed shape)
    if cv2.isContourConvex(contour):
        return True
    
    # Alternatively, check if the start and end points are the same
    start_point = contour[0][0]
    end_point = contour[-1][0]
    return (start_point == end_point).all()

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

def bounding_box(f,original):
    gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    """# print(contours)
    bbox_list = []
    # Loop through contours
    for contour in contours:
        # Check if contour is closed
        if cv2.isContourConvex(contour):
            x, y, w, h = cv2.boundingRect(contour)
            # bbox_list.append((x, y, w, h))
            # Draw the bounding box
            ## cv2.rectangle(original, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.drawContours(original, [contour], -1, (255, 0, 0), 2)
    # return tuple(bbox_list)"""
    
    # Loop through contours
    for contour in contours:
        closed_contour = approximate_and_close_contour(contour)
        x, y, w, h = cv2.boundingRect(closed_contour)
        # bbox_list.append((x, y, w, h))
        # Draw the bounding box
        cv2.rectangle(original, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.rectangle(f, (x, y), (x + w, y + h), (0, 255, 0), 1)
        # if is_contour_closed(closed_contour):
        #     # print("Contour is closed.")
        #     # Draw contour in green
        #     cv2.drawContours(original, [closed_contour], -1, (0, 255, 0), 1)
        # else:
        #     # print("Contour is not closed.")
        #     # Draw contour in red
        #     cv2.drawContours(original, [closed_contour], -1, (0, 0, 255), 1)

        """
        Task that needs to be done:
        - We used contour approx to make it a closed contour
        - eliminate all smaller contours and contours within a bigger contour

        - Since the contour is closed we can find the area aka the # pixels it bounds
        - fine tune lower and upper thresholds to get our traffic light

        - Need to add balck box detection before I try to find traffic lights cuz the assumption is traffic light box is black
            - in morning it can look grayish 
        """
        

cv2.startWindowThread()

# Create main display windows
cv2.namedWindow("Arducam")
cv2.namedWindow("Filtered")

# Create a separate window for HSV trackbars
# Red
cv2.namedWindow("Trackbars_R")
cv2.resizeWindow("Trackbars_R", 290, 250)  # Adjust size for better visibility

# Green
cv2.namedWindow("Trackbars_G")
cv2.resizeWindow("Trackbars_G", 290, 250)  # Adjust size for better visibility

# Yellow
cv2.namedWindow("Trackbars_Y")
cv2.resizeWindow("Trackbars_Y", 290, 250)  # Adjust size for better visibility

# Create trackbar for brightness adjustment in the main display window
cv2.createTrackbar("Brightness", "Arducam", 0, 200, lambda x: None)
cv2.setTrackbarPos("Brightness", "Arducam", 100)

# Create trackbars for three HSV ranges: Red, Green, Yellow
for color in ["R", "G", "Y"]:
    cv2.createTrackbar(f"Low_H_{color}", f"Trackbars_{color}", 0, 179, nothing)  # Lower Hue
    cv2.createTrackbar(f"High_H_{color}", f"Trackbars_{color}", 179, 179, nothing)  # Upper Hue
    cv2.createTrackbar(f"Low_S_{color}", f"Trackbars_{color}", 0, 255, nothing)  # Lower Saturation
    cv2.createTrackbar(f"High_S_{color}", f"Trackbars_{color}", 255, 255, nothing)  # Upper Saturation
    cv2.createTrackbar(f"Low_V_{color}", f"Trackbars_{color}", 0, 255, nothing)  # Lower Value
    cv2.createTrackbar(f"High_V_{color}", f"Trackbars_{color}", 255, 255, nothing)  # Upper Value


color = "R"
cv2.setTrackbarPos(f"Low_H_{color}", f"Trackbars_{color}",0)
cv2.setTrackbarPos(f"High_H_{color}", f"Trackbars_{color}",15)
cv2.setTrackbarPos(f"Low_S_{color}", f"Trackbars_{color}",116)
cv2.setTrackbarPos(f"High_S_{color}", f"Trackbars_{color}",255)
cv2.setTrackbarPos(f"Low_V_{color}", f"Trackbars_{color}",120)
cv2.setTrackbarPos(f"High_V_{color}", f"Trackbars_{color}",255)

color = "G"
cv2.setTrackbarPos(f"Low_H_{color}", f"Trackbars_{color}",63)
cv2.setTrackbarPos(f"High_H_{color}", f"Trackbars_{color}",89)
cv2.setTrackbarPos(f"Low_S_{color}", f"Trackbars_{color}",108)
cv2.setTrackbarPos(f"High_S_{color}", f"Trackbars_{color}",255)
cv2.setTrackbarPos(f"Low_V_{color}", f"Trackbars_{color}",99)
cv2.setTrackbarPos(f"High_V_{color}", f"Trackbars_{color}",255)

color = "Y"
cv2.setTrackbarPos(f"Low_H_{color}", f"Trackbars_{color}",15)
cv2.setTrackbarPos(f"High_H_{color}", f"Trackbars_{color}",35)
cv2.setTrackbarPos(f"Low_S_{color}", f"Trackbars_{color}",125)
cv2.setTrackbarPos(f"High_S_{color}", f"Trackbars_{color}",255)
cv2.setTrackbarPos(f"Low_V_{color}", f"Trackbars_{color}",119)
cv2.setTrackbarPos(f"High_V_{color}", f"Trackbars_{color}",255)
    


# Define camera object
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"format": 'RGB888', "size": (1920, 1080)})
picam2.configure(config)
picam2.start()

picam2.set_controls({"AfMode": 2 ,"AfTrigger": 0})

while True:
    # Read a frame from the Arducam
    frame = picam2.capture_array()
    
    # height, width = frame.shape[:2]
    # frame = frame[:height//2,:]
    # Get brightness trackbar value and adjust brightness

    brightness = cv2.getTrackbarPos("Brightness", "Arducam")
    picam2.set_controls({"Brightness": (brightness - 100)/100})

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Initialize the combined mask
    combined_mask = np.zeros(hsv.shape[:2], dtype="uint8")

    # Loop through the three color ranges (Red, Green, Yellow)
    for color in ["R", "G", "Y"]:
        lower_h = cv2.getTrackbarPos(f"Low_H_{color}", f"Trackbars_{color}")
        upper_h = cv2.getTrackbarPos(f"High_H_{color}", f"Trackbars_{color}")
        lower_s = cv2.getTrackbarPos(f"Low_S_{color}", f"Trackbars_{color}")
        upper_s = cv2.getTrackbarPos(f"High_S_{color}", f"Trackbars_{color}")
        lower_v = cv2.getTrackbarPos(f"Low_V_{color}", f"Trackbars_{color}")
        upper_v = cv2.getTrackbarPos(f"High_V_{color}", f"Trackbars_{color}")
        

        # Define the lower and upper HSV bounds for the current color range
        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        # Create a mask for this color range
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # Combine the masks using bitwise OR
        combined_mask = cv2.bitwise_or(combined_mask, mask)

    # Apply the combined mask to the original frame
    filtered_frame = cv2.bitwise_and(frame, frame, mask=combined_mask)

    # Image processing STEP
    filtered_frame = image_processing(filtered_frame)
    bounding_box(filtered_frame,frame)
    # list_of_bbox = bounding_box(filtered_frame)

    # print(list_of_bbox)

    # for i in list_of_bbox:
    #     cv2.rectangle(frame, (i[0], i[1]), (i[0] + i[2], i[1] + i[3]), (0, 255, 0), 2)

    # Display the frames
    frame = cv2.resize(frame, (640,480))
    filtered_frame = cv2.resize(filtered_frame, (640,480))
    cv2.imshow("Arducam", frame)
    cv2.imshow("Filtered", filtered_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
picam2.stop() 
cv2.destroyAllWindows()




# import cv2
# import numpy as np

# def nothing(x):
#     pass

# def image_processing(f):
#     f = cv2.GaussianBlur(f, (3, 3), 0)
#     return f

# # Initialize the Arducam
# cap = cv2.VideoCapture(0)

# # Create windows
# cv2.namedWindow("Arducam")
# cv2.namedWindow("Color Filter")

# # Create trackbar for brightness adjustment
# cv2.createTrackbar("Brightness", "Arducam", 50, 100, nothing)

# # Create trackbars for HSV adjustment
# cv2.createTrackbar("Lower H", "Color Filter", 0, 179, nothing)
# cv2.createTrackbar("Lower S", "Color Filter", 0, 255, nothing)
# cv2.createTrackbar("Lower V", "Color Filter", 0, 255, nothing)
# cv2.createTrackbar("Upper H", "Color Filter", 179, 179, nothing)
# cv2.createTrackbar("Upper S", "Color Filter", 255, 255, nothing)
# cv2.createTrackbar("Upper V", "Color Filter", 255, 255, nothing)

# while True:
#     # Read a frame from the Arducam
#     ret, frame = cap.read()

#     # Blur input image
#     # frame = image_processing(frame)

#     if not ret:
#         print("Failed to grab frame")
#         break

#     # Get brightness trackbar value and adjust brightness
#     brightness = cv2.getTrackbarPos("Brightness", "Arducam") - 50  # Centered at 0
#     cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)

#     # Convert the frame to HSV color space
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#     # Get HSV trackbar positions
#     lower_h = cv2.getTrackbarPos("Lower H", "Color Filter")
#     lower_s = cv2.getTrackbarPos("Lower S", "Color Filter")
#     lower_v = cv2.getTrackbarPos("Lower V", "Color Filter")
#     upper_h = cv2.getTrackbarPos("Upper H", "Color Filter")
#     upper_s = cv2.getTrackbarPos("Upper S", "Color Filter")
#     upper_v = cv2.getTrackbarPos("Upper V", "Color Filter")

#     # Define the lower and upper HSV range for filtering
#     lower_bound = np.array([lower_h, lower_s, lower_v])
#     upper_bound = np.array([upper_h, upper_s, upper_v])

#     # Create a mask for the colors within the specified range
#     mask = cv2.inRange(hsv, lower_bound, upper_bound)

#     # Apply the mask to the original frame
#     filtered_frame = cv2.bitwise_and(frame, frame, mask=mask)

#     # Display the frames
#     cv2.imshow("Arducam", frame)
#     cv2.imshow("Filtered", filtered_frame)

#     # Break the loop if 'q' is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the capture and close windows
# cap.release()
# cv2.destroyAllWindows()



""" Brightness 43-45
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

"""
-> Apply image processing algorithms like 
        - gaussian blur
        - histogram equilization at night to change gain?
        - opening and closing to join arrow

-> HSV threshold tuning for night and day

-> think of how shape detection will happen at night if color is spread? Check if reducing brightness or gain can work

-> How will you segment and draw bounding box across the images

-> Crop the input image captured so we only use top half of the image.
        - Need to check if Arducam can handle 1080p 30FPS
"""