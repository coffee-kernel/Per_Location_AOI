import os
import time
import threading
import logging
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

class ImageWatcher:
    def __init__(self, folder_path, label_widget, update_interval=0.5):
        self.folder_path = folder_path
        self.label_widget = label_widget
        self.update_interval = update_interval
        self.running = False
        self.latest_file = None

    def start(self):
        """Start watching the folder in a thread"""
        self.running = True
        thread = threading.Thread(target=self._watch_folder, daemon=True)
        thread.start()

    def stop(self):
        """Stop watching the folder"""
        self.running = False

    def _watch_folder(self):
        """Continuously watch the folder for new images"""
        logger.info(f"Watching folder: {self.folder_path}")
        while self.running:
            try:
                files = [f for f in os.listdir(self.folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                if files:
                    # Sort by modified time (newest last)
                    files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(self.folder_path, f)))
                    latest_file = os.path.join(self.folder_path, files[-1])

                    if latest_file != self.latest_file:
                        self.latest_file = latest_file
                        self._update_label_with_image(latest_file)

                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Watcher error: {e}")
                time.sleep(self.update_interval)

    def _update_label_with_image(self, filepath):
        """Load and display the new image in the label full screen size"""
        try:
            # Get screen width & height from the label widget
            screen_w = self.label_widget.winfo_screenwidth()
            screen_h = self.label_widget.winfo_screenheight()

            img = Image.open(filepath)

            # Resize the image to fit screen exactly
            img = img.resize((screen_w, screen_h))

            tk_img = ImageTk.PhotoImage(img)

            # Save reference to avoid garbage collection
            self.label_widget.image = tk_img
            self.label_widget.configure(image=tk_img, width=screen_w, height=screen_h)

            logger.info(f"Displayed new image (resized to {screen_w}x{screen_h}): {filepath}")
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
