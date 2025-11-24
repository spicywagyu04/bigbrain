# **Project: OMNI-OPERATOR**

## **High-Performance Desktop Automation Agent (Mac/Retina Optimized)**

Document Version: 1.0  
Role: Senior Software Design Specification  
Objective: Build a "First Principles" based AI Agent capable of semantic understanding and precise control of a desktop GUI, specifically optimized for Apple Silicon (M1/M2/M3) architectures.

## **I. System Architecture & Modules**

The system follows a **Hybrid Vision-Language Architecture**, designed for high modularity and low coupling.

### **1\. The Visual Cortex (Input Module)**

**Responsibility:** Captures raw visual data from the environment with low latency and handles hardware-specific scaling.

* **ScreenCaptureService**  
  * **Library:** mss (Ultra-fast, cross-platform).  
  * **Function:** Captures raw screen buffers at 60fps potential.  
* **RetinaNormalizer**  
  * **Logic:** Handles the "Logical Point" vs. "Physical Pixel" discrepancy on macOS.  
  * **Mechanism:** Detects NSScreen.backingScaleFactor (typically 2.0 on Retina).  
  * **Formula:** $LogicalPoint \= PhysicalPixel / ScaleFactor$.

### **2\. The Perception Engine (Processing Module)**

**Responsibility:** Converts raw pixels into structured semantic data. Uses a "Fast/Slow" dual-path strategy.

* **Path A: Fast System (The OCR Pipeline)**  
  * **Component:** OCRProcessor  
  * **Engine:** PaddleOCR (English Server Model).  
  * **Role:** Primary method for text-based UI elements (Menus, Buttons, Forms).  
  * **Latency Target:** \< 200ms.  
* **Path B: Slow System (The Vision Pipeline)**  
  * **Component:** VisionGridParser  
  * **Engine:** GPT-4o Vision / Claude 3.5 Sonnet.  
  * **Technique:** Set-of-Mark (SoM) or Grid Overlay.  
  * **Role:** Fallback for icon-only buttons or complex visual reasoning.

### **3\. The Cognitive Core (Reasoning Module)**

**Responsibility:** The "Brain" that maintains context and decides the next action.

* **ContextManager**  
  * **Role:** Maintains a rolling window of Short-Term Memory (STM).  
  * **Data:** Stores the last 5-10 (Observation, Action, Result) tuples to prevent infinite loops.  
* **Planner**  
  * **Role:** Interfaces with the LLM API.  
  * **Input:** User Goal \+ Structured Perception Data.  
  * **Output:** Synthesizes an **Action Plan**.  
* **PromptEngine**  
  * **Role:** Manages System Prompts to ensure strict JSON output formats.

### **4\. The Motor Control (Action Module)**

**Responsibility:** Executes physical interaction with the OS.

* **InputSimulator**  
  * **Library:** pyautogui / Quartz (macOS native).  
  * **Role:** Simulates Mouse Clicks, Drags, Scrolls, and Keyboard Presses.  
* **SafeGuard (The Kill Switch)**  
  * **Role:** Validates coordinates before execution.  
  * **Safety:** Aborts operation if the mouse is jammed to a screen corner. Checks if coordinates are within screen bounds.

### **5\. The Feedback Loop (Verification Module)**

**Responsibility:** Self-correction and error handling.

* **StateDiffAnalyzer**  
  * **Logic:** Compares ScreenState\_T0 (Before Action) vs ScreenState\_T1 (After Action).  
  * **Heuristic:** If pixel difference \< Threshold, assume Action Failed (Stall).  
  * **Recovery:** Triggers a replanning event in the Cognitive Core.

## **II. Step-by-Step Build Process**

We will follow an **Iterative Development Lifecycle**.

### **Phase 1: The Foundation (Infrastructure)**

**Goal:** Build the "Skeleton" that can see and move, but has no brain.

1. **Environment Setup:** Initialize Python environment on Apple Silicon.  
2. **Coordinate Calibration:** Write a script to capture a screenshot, identify a pixel, and move the mouse there.  
   * *Success Metric:* Mouse moves to the exact intended pixel on a Retina display (solving the 2x scaling issue).  
3. **Safety Implementation:** Implement the failsafe mechanism immediately.

### **Phase 2: The Eyes (Perception Implementation)**

**Goal:** Give the agent the ability to read text coordinates accurately.

1. **OCR Integration:** Implement PaddleOCR with the English Server model.  
2. **Coordinate Mapping:** Implement the RetinaNormalizer logic.  
3. **Test Suite:** Create a static screenshot of a complex UI (e.g., VS Code). Write a unit test that asserts the coordinates of specific keywords ("File", "Edit") match reality.

### **Phase 3: The Brain (LLM Integration)**

**Goal:** Connect the Perception layer to the Intelligence layer.

1. **API Setup:** Configure OpenAI/Anthropic clients.  
2. **Prompt Engineering:** Design the System Prompt for strict JSON output.  
   * *Format:* {"action": "click", "target": "File", "reasoning": "User wants to save..."}.  
3. **Mock Execution:** Run the pipeline *without* motor movement. Print intended actions to the console for verification.

### **Phase 4: The Loop (Agent Orchestration)**

**Goal:** Close the OODA Loop (Observe-Orient-Decide-Act).

1. **Main Loop Implementation:**  
   * Capture \-\> OCR \-\> Send to LLM \-\> Parse JSON \-\> Move Mouse \-\> Wait \-\> Repeat.  
2. **Single-Step Testing:** specialized tests for simple commands (e.g., "Open Terminal").  
3. **Latency Optimization:** Profile the loop to identify bottlenecks (image preprocessing vs. API calls).

### **Phase 5: Polish & "The Wow Factor"**

**Goal:** Robustness and advanced features.

1. **SoM Fallback:** Implement visual analysis fallback when OCR fails.  
2. **Voice Feedback:** Add Text-to-Speech (TTS) for status updates.  
3. **Self-Correction:** Implement "Stall Detection" to retry actions if the screen didn't change.

## **III. Proposed Project Structure**

omni-operator/  
├── config/  
│   ├── settings.yaml       \# API keys, screen scale factor, thresholds  
│   └── prompts.yaml        \# System prompts for the LLM  
├── core/  
│   ├── \_\_init\_\_.py  
│   ├── vision.py           \# OCR & Screenshot logic (The Eyes)  
│   ├── brain.py            \# LLM Interface & Planning (The Brain)  
│   ├── motor.py            \# Mouse/Keyboard control (The Hand)  
│   └── retina.py           \# Scaling utilities for Mac M1/M2  
├── tests/  
│   ├── test\_calibration.py \# Verify mouse accuracy  
│   └── test\_ocr.py         \# Verify text recognition  
├── main.py                 \# The entry point (OODA Loop)  
├── requirements.txt        \# Dependencies  
└── README.md

## **IV. Dependencies (requirements.txt)**

\# Core Automation  
pyautogui==0.9.54  
mss==9.0.1  
pyobjc-framework-Quartz; sys\_platform \== 'darwin'  
pyobjc-framework-Cocoa; sys\_platform \== 'darwin'

\# Vision & OCR  
paddlepaddle==2.6.0  
paddleocr==2.7.0.3  
opencv-python==4.9.0.80  
numpy

\# AI & API  
openai\>=1.0.0  
anthropic\>=0.18.0  
pyyaml

\# Utilities  
pillow  
