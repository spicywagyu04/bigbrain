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

    def scan_full(self, image):
        """
        Scans the full image and returns a list of ALL detected elements.
        Each element is a dict: {'text': str, 'center': (log_x, log_y)}
        """
        raw_results = self.ocr.scan(image)
        elements = []

        for line in raw_results:
            # line structure: [[ [x1,y1], [x2,y2], ... ], (text, confidence)]
            box = line[0]
            text = line[1][0]

            # Calculate Center in Physical Pixels
            phys_center_x = (box[0][0] + box[2][0]) / 2
            phys_center_y = (box[0][1] + box[2][1]) / 2

            # Normalize to Logical Points
            log_x, log_y = to_logical(phys_center_x, phys_center_y, self.scale_factor)

            elements.append({
                'text': text,
                'center': (log_x, log_y)
            })

        return elements

    def find_element_in_list(self, ui_elements, target_text):
        """
        Helper to look up coordinates in the already-scanned list.
        Avoids re-running OCR.
        """
        for elem in ui_elements:
            if target_text.lower() in elem['text'].lower():
                return elem['center']
        return None

    def find_element(self, image, target_text):
        """
        Legacy method: Scans image for specific text.
        Now essentially a wrapper around scan_full + find_element_in_list, 
        but kept for backward compatibility or specific checks.
        """
        # We could optimize this to stop at first match, 
        # but scan_full is more useful for the Planner.
        elements = self.scan_full(image)
        return self.find_element_in_list(elements, target_text)
