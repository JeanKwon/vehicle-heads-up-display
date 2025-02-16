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
    if text == "":
        return
    bbox = custom_font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    image = Image.new('RGB', (text_width + 40, text_height + 80), color='black')
    draw = ImageDraw.Draw(image)
    
    arrow_x_center = (text_width+40) // 2
    arrow_y_top = 10
    if direction == "left":
        draw.line([(arrow_x_center - 5, arrow_y_top + 10), (arrow_x_center + 15, arrow_y_top + 10)], fill=constants.FONT_COLOR, width=3)
        draw.line([(arrow_x_center + 10, arrow_y_top + 5), (arrow_x_center + 15, arrow_y_top + 10)], fill=constants.FONT_COLOR, width=3)
        draw.line([(arrow_x_center + 10, arrow_y_top + 15), (arrow_x_center + 15, arrow_y_top + 10)], fill=constants.FONT_COLOR, width=3)
    elif direction == "right":
        draw.line([(arrow_x_center - 15, arrow_y_top + 10), (arrow_x_center + 5, arrow_y_top + 10)], fill=constants.FONT_COLOR, width=3)
        draw.line([(arrow_x_center - 10, arrow_y_top + 5), (arrow_x_center - 15, arrow_y_top + 10)], fill=constants.FONT_COLOR, width=3)
        draw.line([(arrow_x_center - 10, arrow_y_top + 15), (arrow_x_center - 15, arrow_y_top + 10)], fill=constants.FONT_COLOR, width=3)

    text_x = (40) // 2
    text_y = arrow_y_top + 30
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