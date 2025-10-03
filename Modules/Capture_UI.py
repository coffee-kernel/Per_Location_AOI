import customtkinter as ctk
import subprocess
import os
from datetime import datetime
import logging
from threading import Thread
from tkinter import messagebox
import sys
import tkinter as tk
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraApp:
    def __init__(self):
        self.camera_initialized = False

    def initialize_camera(self):
        logger.info("Initializing camera...")
        Thread(target=self._initialize_camera_thread).start()

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
            logger.error(f"Error finding USB device: {str(e)}")
            return None

    def _initialize_camera_thread(self):
        usb_device = self.get_camera_usb_device()
        if usb_device:
            try:
                subprocess.run(["udisksctl", "unmount", "-b", usb_device], capture_output=True, text=True)

                result = subprocess.run(["gphoto2", "--auto-detect"], capture_output=True, text=True)
                if "Canon EOS R10" not in result.stdout and "USB PTP Class Camera" not in result.stdout:
                    logger.error("Camera not detected")
                    return

                result = subprocess.run(["gphoto2", "--summary"], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Camera initialization failed: {result.stderr}")
                    return
                
                logger.info("Camera initialized successfully")
                self.camera_initialized = True
                logger.info("Camera ready!")
            except Exception as e:
                logger.error(f"Initialization error: {str(e)}")
        else:
            logger.error("No Canon camera USB device found")

    def capture_photo(self):
        if not self.camera_initialized:
            logger.error("Error: Camera not initialized")
            return
        
        logger.info("Capturing photo...")
        Thread(target=self._capture_photo_thread).start()

    def _capture_photo_thread(self):
        usb_device = self.get_camera_usb_device()
        if not usb_device:
            logger.error("No Canon camera USB device found")
            return

        try:
            # Attempt to unmount the USB device
            unmount_result = subprocess.run(
                ["udisksctl", "unmount", "-b", usb_device],
                capture_output=True,
                text=True
            )
            if unmount_result.returncode != 0:
                logger.warning(f"Failed to unmount {usb_device}: {unmount_result.stderr}")
            else:
                logger.info(f"Successfully unmounted {usb_device}")

            # Directory where image will be saved
            output_dir = "/home/nvidia/SHARPEYE_DATA/Captured_images"
            os.makedirs(output_dir, exist_ok=True)

            # Check if the directory is writable
            if not os.access(output_dir, os.W_OK):
                logger.error(f"No write permission for directory: {output_dir}")
                return

            # Generate output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"photo_{timestamp}.jpg")

            # Prepare gphoto2 command
            cmd = ["gphoto2", "--capture-image-and-download", f"--filename={output_file}"]
            autodetect_result = subprocess.run(
                ["gphoto2", "--auto-detect"],
                capture_output=True,
                text=True
            )
            if "USB PTP Class Camera" in autodetect_result.stdout:
                cmd = [
                    "gphoto2",
                    "--camera", "Canon EOS R10",
                    "--port", usb_device,
                    "--capture-image-and-download",
                    f"--filename={output_file}"
                ]

            # Capture the photo
            capture_result = subprocess.run(cmd, capture_output=True, text=True)
            if capture_result.returncode == 0:
                logger.info(f"Photo captured and saved to {output_file}")
            else:
                logger.error(f"Capture failed: {capture_result.stderr}")
                return

            # Attempt to remount the USB device
            mount_result = subprocess.run(
                ["udisksctl", "mount", "-b", usb_device],
                capture_output=True,
                text=True
            )
            if mount_result.returncode != 0:
                logger.warning(f"Failed to remount {usb_device}: {mount_result.stderr}")
            else:
                logger.info(f"Successfully remounted {usb_device}")

        except Exception as e:
            logger.error(f"Capture error: {str(e)}")