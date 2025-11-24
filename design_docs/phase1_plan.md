# **Phase 1: Infrastructure & The "Retina Protocol"**

Status: Ready for Implementation  
Goal: Establish a reliable "Body" for the agent that can see (Capture) and act (Click) with 100% pixel-perfect accuracy on macOS Retina displays, while ensuring operational safety.

## **Step 1: The Environment (The "What")**

We need a clean, isolated Python environment. Because we are using paddlepaddle (for OCR later) and pyobjc (for Mac system calls), dependency conflicts are common. We will strictly use a virtual environment.

### **The "How" (Execution)**

1. **Python Version:** Use Python 3.10 or 3.11. (Avoid 3.12+ for now as some ML libraries catch up).  
2. **Virtual Environment Creation:**  
   python3.10 \-m venv venv  
   source venv/bin/activate

3. Dependencies Installation:  
   We need to install the core libraries defined in the architecture.  
   pip install \--upgrade pip  
   pip install pyautogui mss pyobjc-framework-Quartz pyobjc-framework-Cocoa opencv-python  
   \# Note: PaddleOCR will be added in Phase 2, let's keep Phase 1 light.

### **The "Why"**

* **Isolation:** System Python on macOS is protected and messy.  
* **M1/M2 Compatibility:** pyobjc provides the bridge to Apple's native APIs (Cocoa, Quartz), which are essential for getting the true screen scale factor.

## **Step 2: The "Retina Protocol" (The Core Challenge)**

This is the most critical step. If this is wrong, the Agent is functionally blind/clumsy.

### **The "What"**

We need to determine the **Scale Factor**.

* **Physical Pixels:** The actual dots on the screen (what mss captures).  
* **Logical Points:** The coordinates the OS and pyautogui use.  
* **The Equation:** Physical / Scale \= Logical

### **The "How" (Code Implementation)**

We will create core/retina.py.

import Quartz  
from AppKit import NSScreen

def get\_scale\_factor():  
    """  
    Dynamically fetches the backingScaleFactor of the main screen.  
    Returns: float (usually 2.0 for Retina, 1.0 for standard)  
    """  
    screen \= NSScreen.mainScreen()  
    scale \= screen.backingScaleFactor()  
    return scale

def to\_logical(physical\_x, physical\_y, scale\_factor):  
    """  
    Converts OCR coordinates (physical) to Mouse coordinates (logical).  
    """  
    return int(physical\_x / scale\_factor), int(physical\_y / scale\_factor)

### **The "Why"**

* **Hardcoding is Bad:** If you hardcode 2.0, the agent will break if you plug in an external 1080p monitor (which is 1.0). This function makes the agent "monitor-agnostic."

## **Step 3: High-Performance Vision (The Eyes)**

### **The "What"**

We need to capture the screen state. We use mss instead of pyautogui.screenshot() or PIL.ImageGrab.

### **The "How" (Code Implementation)**

We will create core/vision.py.

import mss  
import numpy as np  
import cv2

class Eye:  
    def \_\_init\_\_(self):  
        self.sct \= mss.mss()  
          
    def capture(self):  
        """  
        Captures the primary monitor and returns a numpy array (BGR).  
        """  
        \# monitor 1 is usually the main monitor  
        monitor \= self.sct.monitors\[1\]   
        screenshot \= self.sct.grab(monitor)  
          
        \# Convert to numpy array for OpenCV/PaddleOCR  
        img \= np.array(screenshot)  
          
        \# Drop the Alpha channel (BGRA \-\> BGR) as OCR doesn't need transparency  
        img \= cv2.cvtColor(img, cv2.COLOR\_BGRA2BGR)  
          
        return img

### **The "Why"**

* **Speed:** mss is C-optimized and significantly faster than other Python libraries.  
* **Format:** It returns raw bytes which we can instantly convert to numpy arrays, the native format for AI models. pyautogui returns PIL objects which require slow conversion.

## **Step 4: The Kill Switch (Safety First)**

### **The "What"**

An autonomous agent controlling a mouse can be dangerous. It could accidentally click "Delete", drag files into trash, or close your IDE. We need a hardware-level abort.

### **The "How" (Configuration)**

pyautogui has this built-in, but we must explicitly enable and configure it in core/motor.py.

import pyautogui

class Hand:  
    def \_\_init\_\_(self):  
        \# FAILSAFE: Dragging mouse to any corner throws FailSafeException  
        pyautogui.FAILSAFE \= True   
        \# PAUSE: Add 0.1s delay after every action for stability  
        pyautogui.PAUSE \= 0.1 

    def move\_to(self, x, y):  
        """  
        Moves mouse to logical coordinates (x, y).  
        """  
        try:  
            pyautogui.moveTo(x, y)  
        except pyautogui.FailSafeException:  
            print("🚨 FAILSAFE TRIGGERED. ABORTING AGENT.")  
            exit(1)

    def click(self, x, y):  
        self.move\_to(x, y)  
        pyautogui.click()

### **The "Why"**

* **Panic Button:** When the AI starts "freaking out" (looping rapidly), you can simply slam your mouse to the top-left corner of the screen. The program will crash immediately. This is standard safety protocol for RPA (Robotic Process Automation).

## **Step 5: The "Hello World" Calibration Test**

### **The "What"**

Before we add AI, we must prove the "Body" works. We will write a script that attempts to click a known icon (e.g., the Apple Menu logo at top-left).

### **The "How" (Test Script)**

Create tests/calibration\_test.py.

1. **Manual Check:** Take a screenshot using Mac's native tool (Cmd+Shift+3).  
2. **Measure:** Open it in Preview. Find the Apple Logo. Let's say it's at physical pixel (50, 24).  
3. **Run Script:**  
   * Initialize RetinaNormalizer.  
   * Input Physical (50, 24).  
   * Calculate Logical: (25, 12).  
   * Move Mouse there.  
   * **Pass Condition:** The cursor hovers *exactly* over the Apple Logo.

## **Summary of Files to Create in Phase 1**

1. requirements.txt  
2. core/retina.py (Scaling logic)  
3. core/vision.py (mss capture)  
4. core/motor.py (pyautogui with failsafe)  
5. tests/calibration\_test.py