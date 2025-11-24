import time
import sys
from core.vision import Eye, PerceptionEngine
from core.brain import Planner
from core.motor import Hand

class OmniAgent:
    def __init__(self):
        print("🚀 Initializing OMNI-OPERATOR...")
        self.eye = Eye()
        self.perception = PerceptionEngine()
        self.brain = Planner()
        self.hand = Hand()
        print("✅ Systems Online.")

    def execute_plan(self, plan, ui_elements):
        """
        Translates the JSON plan into physical actions.
        """
        action_type = plan.get("action")
        target_text = plan.get("target_text")
        thought = plan.get("thought")
        
        print(f"🧠 Thinking: {thought}")
        
        if action_type == "click":
            # 1. Locate the element coordinates using Phase 2 logic
            # We search in the passed 'ui_elements' first to save re-scanning
            coords = self.perception.find_element_in_list(ui_elements, target_text)
            
            if coords:
                print(f"🖱️ Clicking '{target_text}' at {coords}")
                self.hand.click(coords[0], coords[1])
            else:
                print(f"❌ Error: Vision lost track of '{target_text}'")
                
        elif action_type == "type":
            # Use "text_to_type" if available, or fallback to "target_text" if the LLM got confused
            text = plan.get("text_to_type") or plan.get("target_text")
            print(f"⌨️ Typing: {text}")
            self.hand.type_text(text)
            
        elif action_type == "done":
            print("🎉 Task Completed successfully.")
            return True # Signal to stop the loop
            
        elif action_type == "fail":
            print("🛑 Agent gave up.")
            return True # Signal to stop
        
        elif action_type == "error":
             print(f"⚠️ Brain Error: {thought}")
             # We don't necessarily stop on error, maybe retry? 
             # For now, let's pause and continue.
             time.sleep(1)
            
        return False # Continue loop

    def run(self, user_goal):
        print(f"🎯 Mission: {user_goal}")
        
        while True:
            try:
                loop_start = time.time()

                # 1. OBSERVE (Phase 1 & 2)
                print("👀 Scanning screen...")
                t0 = time.time()
                screenshot = self.eye.capture()
                t_capture = time.time() - t0
                
                # Get structured data: [{'text': 'File', 'center': (x,y)}, ...]
                t0 = time.time()
                ui_elements = self.perception.scan_full(screenshot)
                t_ocr = time.time() - t0
                
                # 2. ORIENT & DECIDE (Phase 3)
                t0 = time.time()
                plan = self.brain.decide_next_step(user_goal, ui_elements)
                t_think = time.time() - t0
                
                # 3. ACT (Phase 1 & 4)
                t0 = time.time()
                is_finished = self.execute_plan(plan, ui_elements)
                t_act = time.time() - t0
                
                total_time = time.time() - loop_start
                print(f"⏱️  Latency: Capture={t_capture:.2f}s | OCR={t_ocr:.2f}s | Think={t_think:.2f}s | Act={t_act:.2f}s | Total={total_time:.2f}s")
                
                if is_finished:
                    break
                
                # 4. WAIT (Latency Management)
                # Give the UI time to react (e.g., menu opening)
                time.sleep(2.0)
                
            except KeyboardInterrupt:
                print("\n👋 Manual Interruption. Exiting.")
                break

if __name__ == "__main__":
    agent = OmniAgent()
    
    # Simple CLI input for Phase 4
    goal = input("🤖 What would you like me to do? > ")
    
    if goal:
        agent.run(goal)



