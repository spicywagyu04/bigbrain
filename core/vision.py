import mss
import numpy as np
import cv2
from paddleocr import PaddleOCR
import logging
import base64
import json
from core.retina import get_scale_factor, to_logical
# Import LLMClient for VLM fallback. 
# Note: This creates a dependency on core.brain, ensuring core.brain doesn't import core.vision to avoid cycles.
try:
    from core.brain import LLMClient
except ImportError:
    # Handle case where core.brain might not be fully set up or circular import issues during refactors
    LLMClient = None

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
        self.llm_client = None

    def get_llm_client(self):
        if not self.llm_client and LLMClient:
            try:
                self.llm_client = LLMClient()
            except Exception as e:
                print(f"Vision Warning: Could not init LLM for VLM tasks: {e}")
        return self.llm_client

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

    def calculate_diff(self, img1, img2):
        """
        Calculates the Mean Squared Error (MSE) equivalent or pixel change ratio between two images.
        Returns a change ratio (0.0 to 1.0).
        """
        if img1 is None or img2 is None:
            return 0.0
        
        # Ensure same size
        if img1.shape != img2.shape:
            # Resize img2 to match img1 if dimensions differ (unlikely with same screen capture)
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Convert to grayscale to save processing
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Simple subtraction
        diff = cv2.absdiff(gray1, gray2)
        
        # Count non-zero pixels (pixels that changed)
        # We can use a threshold to ignore minor noise
        _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        non_zero_count = np.count_nonzero(diff_thresh)

        total_pixels = gray1.shape[0] * gray1.shape[1]
        change_ratio = non_zero_count / total_pixels

        return change_ratio

    def estimate_coordinates_with_vlm(self, image, target_description):
        """
        Fallback: Asks GPT-4o Vision where the target is.
        Returns logical (x, y) or None.
        """
        client = self.get_llm_client()
        if not client:
            print("❌ VLM Error: No LLM Client available.")
            return None

        # Encode image to base64
        _, buffer = cv2.imencode('.jpg', image)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        height, width = image.shape[:2]

        prompt = f"""
        Look at this screenshot. I need to click on '{target_description}'.
        Estimate the (x, y) coordinates of the center of this element.
        The image size is {width}x{height} (Physical Pixels).
        
        IMPORTANT: 
        - Analyze the visual layout to find the icon or element matching '{target_description}'.
        - Output ONLY valid JSON in this format: {{"x": 123, "y": 456}}
        - Do not output markdown blocks.
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        response_text = client.query(messages)
        if not response_text:
            return None
        
        try:
            data = json.loads(response_text)
            phys_x = data.get("x")
            phys_y = data.get("y")
            
            if phys_x is not None and phys_y is not None:
                # GPT sees the image in its native resolution (Physical Pixels for Retina screenshot)
                # We need to convert these physical pixels back to logical points for the mouse.
                return to_logical(phys_x, phys_y, self.scale_factor)
                
        except json.JSONDecodeError:
            print(f"❌ VLM Error: Could not parse JSON from {response_text}")
            
        return None
