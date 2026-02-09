
import cv2
import os
import datetime
from command_registry import registry
from config import ALLOWED_PATHS

# Use the first allowed path for saving media
MEDIA_PATH = os.path.join(ALLOWED_PATHS[0], "Captured_Media")

@registry.register(name="take_photo", description="Captures a photo from the webcam.", safe=True)
def take_photo():
    """Captures a single frame from the primary camera."""
    if not os.path.exists(MEDIA_PATH):
        os.makedirs(MEDIA_PATH)
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Error: Could not access camera."
        
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(MEDIA_PATH, filename)
        cv2.imwrite(filepath, frame)
        return f"Photo saved to {filepath}"
    else:
        return "Error: Failed to capture image."
