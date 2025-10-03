import subprocess
import cv2

# Your existing code...
device = cv2.cuda.DeviceInfo(0)  # Keep if needed for other checks

def get_gpu_name():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Unknown GPU"  # Fallback if nvidia-smi fails

print(f"GPU: {get_gpu_name()}")