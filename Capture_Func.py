import gphoto2 as gp

# Initialize
camera = gp.Camera()
camera.init()

# Capture and download
file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
print(f"Image captured: {file_path.folder}/{file_path.name}")

# Save to disk
target = open('C:/path/to/save/image.jpg', 'wb')
camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
camera_file.save(target)
target.close()

camera.exit()