import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import constants

def get_signal_color(response):
    if response == 1:
        return constants.RED
    elif response == 2:
        return constants.YELLOW
    elif response == 3:
        return constants.GREEN
    else: 
        return ""

def create_image(custom_font, text, direction):
    if not text:
        return

    # Measure the text size
    bbox = custom_font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create the blank image
    image = Image.new('RGB', (text_width + 100, text_height + 120), color='black')
    draw = ImageDraw.Draw(image)

    # -------------------------------------------------------
    # Arrow dimensions
    # -------------------------------------------------------
    arrow_height      = 20   # The rectangle's height (shaft)
    arrow_rect_length = 40   # The rectangle's width (shaft)
    arrow_tip_length  = 40   # The triangle's horizontal length
    triangle_extend   = 10   # How much taller the triangle is (top & bottom) than the rectangle

    arrow_x_center = (text_width + 100) // 2
    arrow_y_top    = 10
    arrow_y_bottom = arrow_y_top + arrow_height

    # The total horizontal width of the arrow shape
    total_arrow_width = arrow_rect_length + arrow_tip_length
    arrow_x_start = arrow_x_center - (total_arrow_width // 2)

    # Draw the arrow
    if direction == "left":
        # Label says "left" but we visually point RIGHT.

        # 1) Rectangle (shaft)
        rect_coords = [
            (arrow_x_start, arrow_y_top),  
            (arrow_x_start + arrow_rect_length, arrow_y_bottom)
        ]
        draw.rectangle(rect_coords, fill=constants.FONT_COLOR)

        # 2) Triangle (head) on the right
        #
        #    Notice how the 'triangle_extend' makes the top corner 
        #    go above 'arrow_y_top' and bottom corner go below 'arrow_y_bottom'
        #    so that the vertical side is taller than the rectangle’s height.
        triangle_coords = [
            (arrow_x_start + arrow_rect_length, arrow_y_top - triangle_extend),      # extended top
            (arrow_x_start + arrow_rect_length + arrow_tip_length, 
             arrow_y_top + arrow_height // 2),                                      # center tip
            (arrow_x_start + arrow_rect_length, arrow_y_bottom + triangle_extend)    # extended bottom
        ]
        draw.polygon(triangle_coords, fill=constants.FONT_COLOR)

    elif direction == "right":
        # Label says "right" but we visually point LEFT.

        # 1) Rectangle (shaft)
        rect_coords = [
            (arrow_x_start + arrow_tip_length, arrow_y_top),
            (arrow_x_start + arrow_tip_length + arrow_rect_length, arrow_y_bottom)
        ]
        draw.rectangle(rect_coords, fill=constants.FONT_COLOR)

        # 2) Triangle (head) on the left
        triangle_coords = [
            (arrow_x_start + arrow_tip_length, arrow_y_top - triangle_extend), 
            (arrow_x_start, arrow_y_top + arrow_height // 2),
            (arrow_x_start + arrow_tip_length, arrow_y_bottom + triangle_extend)
        ]
        draw.polygon(triangle_coords, fill=constants.FONT_COLOR)

    # Draw the text below the arrow
    text_x = 50
    text_y = arrow_y_bottom + 20
    draw.text((text_x, text_y), text, font=custom_font, fill=constants.FONT_COLOR)

    return ImageTk.PhotoImage(image)

def display_forward_signal(root, custom_font, color):
    text = get_signal_color(color)
    photo = create_image(custom_font, text, "forward")
    label_forward_signal = tk.Label(root, image=photo, bg='black')
    label_forward_signal.image = photo
    label_forward_signal.place(relx=0.5, y=10, anchor='n')

def display_left_signal(root, custom_font, color):
    text = get_signal_color(color)
    photo = create_image(custom_font, text, "left")
    label_left_signal = tk.Label(root, image=photo, bg='black')
    label_left_signal.image = photo
    label_left_signal.place(relx=1.0, y=10, anchor='ne')

def display_right_signal(root, custom_font, color):
    text = get_signal_color(color)
    photo = create_image(custom_font, text, "right")
    label_right_signal = tk.Label(root, image=photo, bg='black')
    label_right_signal.image = photo
    label_right_signal.place(x=10, y=10, anchor='nw')
    
def display_speed(root, custom_font, current_speed):
    text = f"hpm {round(current_speed)}"
    if not text:
        return

    # Measure text size with the PIL font
    bbox = custom_font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create a PIL image for the text
    x_margin = 20
    y_margin = 20
    image_width = text_width + x_margin * 2
    image_height = text_height + y_margin * 2

    # Black background
    image = Image.new('RGB', (image_width, image_height), color='black')
    draw = ImageDraw.Draw(image)

    # Write the text with the same custom PIL font & color
    draw.text((x_margin, y_margin), text, font=custom_font, fill=constants.FONT_COLOR)

    # Convert to a PhotoImage
    photo = ImageTk.PhotoImage(image)

    # Place a label containing this image at bottom-left
    label_speed = tk.Label(root, image=photo, bg='black')
    label_speed.image = photo  # keep a reference to avoid GC
    label_speed.place(relx=1.0, rely=1.0, anchor='se', x=10, y=-10)