from tkinter import messagebox, filedialog
import time
import json
from PIL import Image, ImageTk
import re
import os


def handle_upload(canvas, root, app):
    """Handle uploading an image and displaying it on the canvas."""
    try:
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.JPG")]
        )

        if not file_path:
            return  # User canceled the file dialog

        # Open and resize the image
        app.original_image = Image.open(file_path)
        frame_width = root.winfo_width()
        frame_height = root.winfo_height()

        # Resize the image while maintaining aspect ratio
        app.original_image.thumbnail((frame_width, frame_height))

        # Convert the image to a PhotoImage for display
        app.displayed_image = ImageTk.PhotoImage(app.original_image)

        # Display the image on the canvas
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=app.displayed_image)
        canvas.image_ref = app.displayed_image  # Prevent garbage collection

        print(f"Image uploaded successfully: {file_path}")
    except Exception as e:
        print(f"Error uploading image: {e}")


def start_drawing(event, app):
    # Record the starting point for rectangle drawing
    app.start_x = event.x
    app.start_y = event.y

    # Create a placeholder for the rectangle object (to be updated on motion)
    app.current_rectangle = app.canvas.create_rectangle(
        app.start_x, app.start_y, event.x, event.y, outline="red", width=3
    )


def update_rectangle(event, app):
    # Update the rectangle dynamically as the mouse moves
    if app.current_rectangle is not None:
        app.canvas.coords(
            app.current_rectangle,
            app.start_x, app.start_y,
            event.x, event.y
        )


def finish_drawing(event, app):
    # Finalize the rectangle drawing: save its coordinates if needed
    if app.current_rectangle is not None:
        coords = app.canvas.coords(app.current_rectangle)  # Get rectangle coordinates
        x1, y1, x2, y2 = coords
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # get serial number value
        serial_number = app.serial_entry.get().strip()
        if not serial_number:
            messagebox.showwarning("Warning", "Serial Number is Empty!")
            app.canvas.delete(app.current_rectangle)
            app.current_rectangle = None
            return
        
        # sanitize input
        serial_number = re.sub(r'[^\w\-]', '_', serial_number)
        
        # generate filename
        roi_filename = f"ROI_Image_{serial_number}.png"
        roi_filepath = os.path.join("Data", "ROI_Images", roi_filename)
        
        os.makedirs(os.path.dirname(roi_filepath), exist_ok=True)
        
        try:
            if hasattr(app, "original_image"):
                roi_image = app.original_image.crop((x, y, x + width, y + height))
                roi_image.save(roi_filepath)
                print(f"ROI saved as {roi_filepath}")
            else:
                print("Original image not found. Cannot save ROI.")
                roi_filename = "N/A"
        except Exception as e:
            print(f"Error saving ROI: {e}")
            roi_filename = "N/A"
            
        # store ROI data with filename
        roi = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "ROI_image_timestamp": roi_filename
        }
        
        app.roi_list = getattr(app, "roi_list", [])
        app.roi_list.append(roi)
        
        print(f"Rectangle finalized with coordinates: x={x}, y={y}, width={width}, height={height}, filename={roi_filename}")
        
        app.drawn_rectangles.append(app.current_rectangle)
        app.current_rectangle = None
        
def handle_clear(canvas, serial_entry, app):
    # get the serial number for json filename
    serial_number = serial_entry.get().strip()
    
    if not serial_entry or not (hasattr(app, "roi_list") and app.roi_list):
        messagebox.showinfo("Info", "No ROIs to save or Serial Number is empty!")
        canvas.delete("all")
        app.drawn_rectangles.clear()
        app.roi_list = []
        serial_entry.delete(0, 'end')
        return

    json_filename = f"{serial_number}.json"
    json_filepath = os.path.join("Data", "JSON", json_filename)
    
    os.makedirs(os.path.dirname(json_filepath), exist_ok=True)
    try:
        with open(json_filepath, 'w') as f:
            json.dump(app.roi_list, f, indent=4)
        print(f"ROI coordinates and filenames saved to {json_filepath}")
    except Exception as e:
        print(f"Error saving ROI coordinates: {e}")

    canvas.delete("all")
    app.drawn_rectangles.clear()
    app.roi_list = []
    serial_entry.delete(0, 'end')
    
    messagebox.showinfo("Info", "Saved ROI coordinates and cleared canvas.")