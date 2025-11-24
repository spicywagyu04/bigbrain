# **Phase 5: Advanced Perception & Self-Correction**

Status: Ready for Implementation  
Goal: To elevate the agent from a brittle script executor to a robust, self-healing system by integrating Vision Large Models (VLMs) for non-textual elements, Text-to-Speech (TTS) for user feedback, and visual diffing for error detection.

## **Step 1: The Visual Fallback (The "What")**

In Phase 2, we relied on OCR. But what if the user says "Click the Trash Can icon"? OCR sees nothing. We need a "Slow System" fallback that uses GPT-4o Vision or Claude 3.5 Sonnet to semantically understand icons and images.

### **The "How" (Implementation Strategy)**

We will modify core/vision.py to include a VLM-based estimator.

1. The Grid Strategy (Simplest Robust Method):  
   Instead of complex Set-of-Mark (SoM) overlays immediately, we can use a normalized coordinate estimation prompt.  
2. **Code Logic (core/brain.py or core/vision.py):**  
   \# core/vision.py updates

   def estimate\_coordinates\_with\_vlm(self, image\_path, target\_description):  
       """  
       Fallback: Asks GPT-4o Vision where the target is.  
       Returns logical (x, y).  
       """  
       \# Encode image to base64  
       base64\_image \= encode\_image(image\_path)

       prompt \= f"""  
       Look at this screenshot. I need to click on '{target\_description}'.  
       Estimate the (x, y) coordinates of the center of this element.  
       The image size is {width}x{height}.  
       Output ONLY JSON: {{"x": 100, "y": 200}}  
       """

       \# Call LLMClient (Brain) with image payload  
       \# Parse JSON  
       \# Apply Retina Scaling (Divide by 2.0 if needed, though GPT usually sees the logical resolution if resized)  
       return coords

3. Integration in main.py:  
   Update the execute\_plan method. If find\_element\_in\_list (OCR) fails, trigger estimate\_coordinates\_with\_vlm (Vision).

### **The "Why"**

* **Semantic Understanding:** OCR is blind to shapes. VLMs bridge the gap between "Read" and "See".  
* **Graceful Degradation:** The system tries the fast method (OCR \~200ms) first. Only if that fails does it pay the cost for the slow method (VLM \~3s).

## **Step 2: The Auditory Interface (The "What")**

A silent agent is terrifying. You don't know if it's thinking, frozen, or about to delete your files. We need auditory feedback.

### **The "How" (Implementation Strategy)**

We will use pyttsx3, a lightweight, offline, cross-platform Text-to-Speech library.

1. **Install Dependency:**  
   pip install pyttsx3

2. **Module Creation (core/voice.py):**  
   import pyttsx3  
   import threading

   class Voice:  
       def \_\_init\_\_(self):  
           self.engine \= pyttsx3.init()  
           \# Select a voice (usually index 0 or 1 for standard OS voices)  
           self.engine.setProperty('rate', 170\) \# Speed up slightly

       def speak(self, text):  
           """  
           Non-blocking speak function.  
           """  
           def \_run():  
               self.engine.say(text)  
               self.engine.runAndWait()

           \# Run in separate thread to not block the OODA loop  
           threading.Thread(target=\_run).start()

3. **Hooking into Main:**  
   * **Startup:** "Systems Online."  
   * **Thinking:** "Searching for File menu..."  
   * **Success:** "Task Complete."  
   * **Error:** "I cannot find the target."

### **The "Why"**

* **User Trust:** Hearing the agent's intent *before* it moves the mouse gives the user a chance to abort (Kill Switch) if the intent is wrong.  
* **Debugging:** It acts as a real-time log you don't have to read.

## **Step 3: The Autonomic Nervous System (Stall Detection) (The "What")**

If the agent clicks "Save", but the "Save" window doesn't open, a naive agent will assume success and move on, causing a cascade of errors. We need to verify that the screen *changed*.

### **The "How" (Implementation Strategy)**

We compare the pixel state before and after an action.

1. **State Diffing Logic:**  
   \# core/vision.py

   def calculate\_diff(self, img1, img2):  
       """  
       Calculates the Mean Squared Error (MSE) between two images.  
       Returns a similarity score (0.0 to 1.0).  
       """  
       \# Convert to grayscale to save processing  
       gray1 \= cv2.cvtColor(img1, cv2.COLOR\_BGR2GRAY)  
       gray2 \= cv2.cvtColor(img2, cv2.COLOR\_BGR2GRAY)

       \# Simple subtraction  
       diff \= cv2.absdiff(gray1, gray2)  
       non\_zero\_count \= np.count\_nonzero(diff)

       \# If less than 1% of pixels changed, it's a stall  
       total\_pixels \= gray1.shape\[0\] \* gray1.shape\[1\]  
       change\_ratio \= non\_zero\_count / total\_pixels

       return change\_ratio

2. **The Loop Update (main.py):**  
   \# In run() loop:  
   screenshot\_before \= self.eye.capture()  
   self.execute\_plan(...)  
   time.sleep(2.0) \# Wait for UI animation  
   screenshot\_after \= self.eye.capture()

   change\_ratio \= self.perception.calculate\_diff(screenshot\_before, screenshot\_after)

   if change\_ratio \< 0.001: \# Threshold: 0.1% change  
       print("⚠️ Warning: Screen didn't change. Action might have failed.")  
       self.voice.speak("I don't think that click worked.")  
       \# Trigger Retry Logic or ask Brain to re-plan

### **The "Why"**

* **Closed-Loop Control:** This transitions the system from "Open Loop" (Hope it worked) to "Closed Loop" (Verify it worked). This is standard control theory applied to AI Agents.

## **Summary of Files to Modify/Create in Phase 5**

1. **core/voice.py**: New module for TTS.  
2. **core/vision.py**: Update with calculate\_diff and estimate\_coordinates\_with\_vlm.  
3. **main.py**: Integrate the voice feedback and the state-diff check in the main loop.  
4. **requirements.txt**: Add pyttsx3.

## **Final Project Checklist**

At the end of Phase 5, your **OMNI-OPERATOR** will:

1. \[x\] **See** text on Retina screens perfectly (Phase 1 & 2).  
2. \[x\] **Understand** complex user intents via LLM (Phase 3).  
3. \[x\] **Act** safely with a hardware kill-switch (Phase 1 & 4).  
4. \[x\] **Speak** its status to you (Phase 5).  
5. \[x\] **Self-Correct** if actions fail (Phase 5).  
6. \[x\] **See Icons** when text fails (Phase 5).

You are now ready to build the ultimate desktop automation tool.