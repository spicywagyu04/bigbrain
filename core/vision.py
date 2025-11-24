import mss
import numpy as np
import cv2
from paddleocr import PaddleOCR
import logging
from core.retina import get_scale_factor, to_logical

# Suppress verbose logging from Paddle
logging.getLogger("ppocr").setLevel(logging.ERROR)

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

class OCRProcessor:
    def __init__(self):
        # Initialize the English server-scale model for maximum accuracy.
        # 'use_angle_cls=True' enables detection of rotated text,
        # though less critical for standard UI, it adds robustness.
        self.ocr_engine = PaddleOCR(
            use_angle_cls=True, 
            lang='en'
        )

    def scan(self, image_array):
        """
        Performs OCR on the provided numpy image array.
        Returns a raw list of detected elements including bounding boxes and text.
        """
        # The model expects a BGR numpy array (standard from cv2/mss)
        result = self.ocr_engine.ocr(image_array, cls=True)

        # PaddleOCR returns a list of lists; handle empty results safely.
        if not result or result[0] is None:
            return []

        return result[0]

class PerceptionEngine:
    def __init__(self):
        self.ocr = OCRProcessor()
        self.scale_factor = get_scale_factor()

    def find_element(self, image, target_text):
        """
        Scans the image for target_text and returns the LOGICAL center coordinates.
        Returns: (x, y) tuple or None if not found.
        """
        raw_results = self.ocr.scan(image)

        for line in raw_results:
            # line structure: [[ [x1,y1], [x2,y2], ... ], (text, confidence)]
            box = line[0]
            text = line[1][0]

            # Case-insensitive fuzzy matching
            if target_text.lower() in text.lower():
                # 1. Calculate Center in Physical Pixels
                # Box[0] is top-left, Box[2] is bottom-right
                phys_center_x = (box[0][0] + box[2][0]) / 2
                phys_center_y = (box[0][1] + box[2][1]) / 2

                # 2. Normalize to Logical Points (The Retina Protocol)
                log_x, log_y = to_logical(phys_center_x, phys_center_y, self.scale_factor)

                return (log_x, log_y)

        return None
