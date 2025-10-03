import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import re

class CameraDisplay:
    def __init__(self, root, canvas, screen_width, screen_height):
        self.root = root
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.DEVICE_PATH = '/dev/video0'
        self.running = False
        self.is_annotating = False
        self.current_frame = None
        self.cap = None

        # GStreamer pipeline
        self.pipeline = (
            f"v4l2src device={self.DEVICE_PATH} ! "
            "image/jpeg,width=1920,height=1080,framerate=60/1 ! "
            "jpegdec ! video/x-raw ! "
            "nvvidconv ! video/x-raw,format=BGRx ! "
            "videoconvert ! video/x-raw,format=BGR ! "
            "appsink"
        )

        self.show_video()

    # Rest of the class methods (initialize_capture, display_frame, etc.) remain unchanged
    def initialize_capture(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            error_msg = (
                f"Error: Could not open device {self.DEVICE_PATH}. "
                "Device may be busy or pipeline is incorrect.\n"
                f"Test pipeline: gst-launch-1.0 {self.pipeline.replace('appsink', 'autovideosink')}\n"
                "Check: lsof /dev/video0 and kill any processes using it.\n"
                "Verify formats: v4l2-ctl --list-formats-ext -d /dev/video0"
            )
            messagebox.showwarning("Info", f"{error_msg}")
            print(error_msg)
            return False
        return True
    
    # get the USB camera device
    def get_camera_usb_device(self):
        try:
            result = subprocess.run(["lsusb"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "Canon" in line:
                    match = re.search(r"Bus (\d+) Device (\d+)", line)
                    if match:
                        bus, dev = match.groups()
                        return f"/dev/bus/usb/{bus}/{dev}"
            return None
        except Exception as e:
            print(f"Error finding USB device: {str(e)}")
            return None
    
    # unmount usb storage
    def unmount_usb_storage(self):
        usb_device = self.get_camera_usb_device()
        if usb_device:
            subprocess.run(["udisksctl", "unmount", "-b", usb_device], capture_output=True, text=True)
        else:
            print("No USB device detected!")

    # mount the usb storage
    def mount_usb_storage(self):
        usb_device = self.get_camera_usb_device()
        if usb_device:
            subprocess.run(["udisksctl", "mount", "-b", usb_device], capture_output=True, text=True)
        else:
            print("No USB device detected!")

    def display_frame(self, frame):
        self.canvas.update()
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)
        frame_height, frame_width = frame.shape[:2]
        scale = min(canvas_width / frame_width, canvas_height / frame_height)
        new_width = int(frame_width * scale)
        new_height = int(frame_height * scale)
        frame = cv2.resize(frame, (new_width, new_height))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo)
        self.canvas.image = photo

    def update_video(self):
        if not self.running or self.is_annotating:
            return
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            self.hide_video()
            return
        self.current_frame = frame
        self.display_frame(frame)
        self.root.after(33, self.update_video)

    def hide_video(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.canvas.delete("all")
        print("Video live viewing is hidden.")

    def show_video(self):
        if self.initialize_capture():
            self.running = True
            print("Video live viewing is active.")
            self.update_video()

    def __del__(self):
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()