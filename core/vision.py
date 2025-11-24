import mss
import numpy as np
import cv2

class Eye:
    def __init__(self):
        self.sct = mss.mss()
        
    def capture(self):
        """
        Captures the primary monitor and returns a numpy array (BGR).
        """
        # monitor 1 is usually the main monitor
        monitor = self.sct.monitors[1] 
        screenshot = self.sct.grab(monitor)
        
        # Convert to numpy array for OpenCV/PaddleOCR
        img = np.array(screenshot)
        
        # Drop the Alpha channel (BGRA -> BGR) as OCR doesn't need transparency
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img

