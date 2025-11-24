# **Phase 2: Perception Engine & Ocular Calibration**

Status: Ready for Implementation  
Goal: To engineer the "Visual Cortex" of the agent, enabling it to semantically interpret screen textual elements and map them to actionable, logical coordinates with pixel-perfect precision on High-DPI (Retina) architectures.

## **Step 1: The Neural OCR Integration (The "What")**

The objective is to integrate a robust Optical Character Recognition (OCR) engine capable of detecting and recognizing text within the high-resolution screenshots captured by the mss library. We have selected PaddleOCR for this purpose due to its superior performance on English UI elements compared to traditional engines like Tesseract.

### **The "How" (Implementation Strategy)**

1. Dependency Configuration:  
   Ensure the paddlepaddle and paddleocr libraries are correctly installed within the virtual environment. Note that on Apple Silicon (M1/M2/M3), specific installation commands may be required to leverage the ARM64 architecture.  
   pip install paddlepaddle paddleocr

2. Module Development (core/vision.py):  
   We will expand the existing vision.py module to include the OCRProcessor class. This class will encapsulate the PaddleOCR model initialization and the inference logic.  
   from paddleocr import PaddleOCR  
   import logging

   \# Suppress verbose logging from Paddle  
   logging.getLogger("ppocr").setLevel(logging.ERROR)

   class OCRProcessor:  
       def \_\_init\_\_(self):  
           \# Initialize the English server-scale model for maximum accuracy.  
           \# 'use\_angle\_cls=True' enables detection of rotated text,   
           \# though less critical for standard UI, it adds robustness.  
           self.ocr\_engine \= PaddleOCR(  
               use\_angle\_cls=True,   
               lang='en',   
               show\_log=False  
           )

       def scan(self, image\_array):  
           """  
           Performs OCR on the provided numpy image array.  
           Returns a raw list of detected elements including bounding boxes and text.  
           """  
           \# The model expects a BGR numpy array (standard from cv2/mss)  
           result \= self.ocr\_engine.ocr(image\_array, cls=True)

           \# PaddleOCR returns a list of lists; handle empty results safely.  
           if not result or result\[0\] is None:  
               return \[\]

           return result\[0\]

### **The "Why"**

* **Accuracy:** UI text is often small and sans-serif. Deep learning-based models like PaddleOCR significantly outperform heuristic-based models in these scenarios.  
* **Latency:** The lightweight English server model offers an optimal trade-off between inference speed (crucial for the agent's reaction time) and recognition precision.

## **Step 2: The Retina Integration Strategy (The "What")**

This step bridges the gap between the "Physical World" (the raw pixels seen by the OCR) and the "Logical World" (the coordinate system used by the Operating System). Without this normalization, the agent would consistently misinterpret the location of UI elements on Retina displays.

### **The "How" (Implementation Strategy)**

We must modify the perception logic to utilize the RetinaNormalizer utility developed in Phase 1\. The Vision module will now depend on the core.retina module.

1. Coordinate Transformation Logic:  
   When the OCR engine returns a bounding box, it is defined in physical pixels (e.g., x=2000 on a 2x scaled screen). We must calculate the center point of this box and then divide it by the system's scale factor.  
   \# Inside core/vision.py  
   from core.retina import get\_scale\_factor, to\_logical

   class PerceptionEngine:  
       def \_\_init\_\_(self):  
           self.ocr \= OCRProcessor()  
           self.scale\_factor \= get\_scale\_factor()

       def find\_element(self, image, target\_text):  
           """  
           Scans the image for target\_text and returns the LOGICAL center coordinates.  
           """  
           raw\_results \= self.ocr.scan(image)

           for line in raw\_results:  
               \# line structure: \[\[ \[x1,y1\], \[x2,y2\], ... \], (text, confidence)\]  
               box \= line\[0\]  
               text \= line\[1\]\[0\]

               \# Case-insensitive fuzzy matching  
               if target\_text.lower() in text.lower():  
                   \# 1\. Calculate Center in Physical Pixels  
                   \# Box\[0\] is top-left, Box\[2\] is bottom-right  
                   phys\_center\_x \= (box\[0\]\[0\] \+ box\[2\]\[0\]) / 2  
                   phys\_center\_y \= (box\[0\]\[1\] \+ box\[2\]\[1\]) / 2

                   \# 2\. Normalize to Logical Points (The Retina Protocol)  
                   log\_x, log\_y \= to\_logical(phys\_center\_x, phys\_center\_y, self.scale\_factor)

                   return (log\_x, log\_y)

           return None

### **The "Why"**

* **Abstraction:** By handling the scaling logic within the PerceptionEngine, the higher-level "Brain" module does not need to be aware of hardware specifics. It simply requests "Where is 'File'?" and receives valid OS coordinates.  
* **Precision:** Calculating the center point *before* scaling minimizes rounding errors that could occur if we scaled the corners individually.

## **Step 3: The Semantic Targeting Protocol (The "What")**

The agent must be able to locate elements even if the OCR output is imperfect or if the query is slightly ambiguous. This requires a robust search mechanism rather than simple exact string matching.

### **The "How" (Implementation Strategy)**

The search logic should implement **Case-Insensitive Substring Matching**.

* Implementation:  
  Instead of if target \== detected\_text, use if target.lower() in detected\_text.lower().  
* Advanced Consideration (Future Proofing):  
  For Phase 2, simple substring matching is sufficient. In later phases, we may introduce Levenshtein Distance (fuzzy string matching) to handle minor OCR typos (e.g., recognizing "F1le" instead of "File").

### **The "Why"**

* **Robustness:** Users may prompt "Click File", while the OCR might read "File " (with a trailing space) or "FILE". Strict equality checks would cause the agent to fail unnecessarily.

## **Step 4: The Validation Protocol (The "What")**

Before connecting the "Brain" (LLM), we must scientifically verify that the "Eyes" are functioning correctly. We will create a unit test that decouples vision from motor control.

### **The "How" (Testing Strategy)**

Create tests/test\_perception.py:

1. **Artifact Creation:** Manually capture a screenshot of a known application (e.g., the Terminal window) and save it as tests/assets/terminal\_sample.png.  
2. **Ground Truth Definition:** Open the image in an editor and record the logical coordinates of a specific word, such as "Shell".  
3. **Automated Assertion:**  
   import cv2  
   from core.vision import PerceptionEngine

   def test\_find\_shell\_coordinates():  
       \# Initialize Engine  
       engine \= PerceptionEngine()

       \# Load static asset (simulate screen capture)  
       img \= cv2.imread("tests/assets/terminal\_sample.png")

       \# Execute Search  
       coords \= engine.find\_element(img, "Shell")

       \# Assertions  
       assert coords is not None, "Failed to detect text 'Shell'"  
       print(f"Detected Coordinates: {coords}")  
       \# Add tolerance logic (e.g., \+/- 10 pixels) for pass/fail

### **The "Why"**

* **Isolation:** This test proves the OCR and Scaling logic work independently of the screen capture or mouse movement modules.  
* **Reproducibility:** Using a static image ensures the test passes consistently, regardless of what is actually on the developer's screen during the test run.

## **Summary of Files to Modify/Create in Phase 2**

1. **core/vision.py**: Update to include OCRProcessor and PerceptionEngine classes.  
2. **core/retina.py**: Ensure get\_scale\_factor is accessible.  
3. **tests/test\_perception.py**: New test file for validating OCR logic.  
4. **tests/assets/**: Directory for storing static test screenshots.