from tkinter import messagebox, filedialog
import time
import json
from PIL import Image, ImageTk


def handle_upload(canvas, root):
    """Handle uploading an image and displaying it on the canvas."""
    try:
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if not file_path:
            return  # User canceled the file dialog

        # Open and resize the image
        img = Image.open(file_path)
        frame_width = root.winfo_width()
        frame_height = root.winfo_height()

        # Resize the image while maintaining aspect ratio
        img.thumbnail((frame_width, frame_height))

        # Convert the image to a PhotoImage for display
        displayed_image = ImageTk.PhotoImage(img)

        # Display the image on the canvas
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=displayed_image)
        canvas.image_ref = displayed_image  # Prevent garbage collection

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
    # Finalize the rectangle drawing: save its coordinates and crop ROI
    if app.current_rectangle is not None:
        coords = app.canvas.coords(app.current_rectangle)  # Get rectangle coordinates
        x1, y1, x2, y2 = coords
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # Generate timestamp for ROI filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        roi_filename = f"ROI_Image_{timestamp}.png"
        save_path = f"/home/nvidia/Main_Folder/Inspected_images/Captured_Images/{roi_filename}"

        try:
            if hasattr(app, "original_image") and app.original_image is not None:
                # Get original image dimensions
                original_width, original_height = app.original_image.size

                # Get displayed image dimensions
                displayed_width = getattr(app, "displayed_image_width", app.canvas.winfo_width())
                displayed_height = getattr(app, "displayed_image_height", app.canvas.winfo_height())

                if displayed_width <= 1 or displayed_height <= 1:
                    displayed_width = app.root.winfo_screenwidth() - 40
                    displayed_height = app.root.winfo_screenheight() - 140
                    print(f"Using fallback dimensions: {displayed_width}x{displayed_height}")

                # Get image offsets
                offset_x = getattr(app, "image_offset_x", 0)
                offset_y = getattr(app, "image_offset_y", 0)

                # Adjust coordinates for offset (convert canvas coords to image coords)
                image_x = x - offset_x
                image_y = y - offset_y

                # Calculate scaling factors
                scale_x = original_width / displayed_width
                scale_y = original_height / displayed_height

                # Scale the coordinates to the original image's dimensions
                scaled_x = int(image_x * scale_x)
                scaled_y = int(image_y * scale_y)
                scaled_width = int(width * scale_x)
                scaled_height = int(height * scale_y)

                # Ensure scaled coordinates are within image bounds
                scaled_x = max(0, min(scaled_x, original_width - 1))
                scaled_y = max(0, min(scaled_y, original_height - 1))
                scaled_width = min(scaled_width, original_width - scaled_x)
                scaled_height = min(scaled_height, original_height - scaled_y)

                # Crop the ROI from the original image
                roi_image = app.original_image.crop((
                    scaled_x, scaled_y,
                    scaled_x + scaled_width, scaled_y + scaled_height
                ))
                roi_image.save(save_path)
                print(f"ROI saved as {save_path}")
            else:
                print("Original image not found or not set. Cannot save ROI.")
                roi_filename = "N/A"
                save_path = "N/A"
        except Exception as e:
            print(f"Error saving ROI: {e}")
            roi_filename = "N/A"
            save_path = "N/A"

        # Store ROI data with filename
        roi = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "image_x": image_x,
            "image_y": image_y,
            "scaled_x": scaled_x,
            "scaled_y": scaled_y,
            "scaled_width": scaled_width,
            "scaled_height": scaled_height,
            "ROI_image_timestamp": roi_filename,
            "ROI_save_path": save_path
        }

        app.roi_list = getattr(app, "roi_list", [])
        app.roi_list.append(roi)

        print(f"Rectangle finalized with coordinates: x={x}, y={y}, width={width}, height={height}, "
              f"image: x={image_x}, y={image_y}, "
              f"scaled: x={scaled_x}, y={scaled_y}, width={scaled_width}, height={scaled_height}, "
              f"filename={save_path}")

        app.drawn_rectangles.append(app.current_rectangle)
        app.current_rectangle = None
        
def handle_clear(canvas, serial_entry, app):
    if hasattr(app, "roi_list") and app.roi_list:
        try:
            with open("roi_coordinates.json", 'w') as f:
                json.dump(app.roi_list, f, indent=4)
            print("ROI coordinates saved to roi_coordinates.json")
        except Exception as e:
            print(f"Error saving ROI coordinates: {e}")

    canvas.delete("all")
    app.drawn_rectangles.clear()
    app.roi_list = []
    serial_entry.delete(0, 'end')
    
    messagebox.showinfo("Info", "Saved ROI coordinates and cleared canvas.")