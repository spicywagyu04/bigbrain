import os
import json
from openai import OpenAI
from core.prompts import SYSTEM_PROMPT

class LLMClient:
    def __init__(self):
        # Initialize the client with the API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Default to GPT-4o

    def query(self, messages):
        """
        Sends a structured conversation to the LLM and returns the response.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}, # Crucial for stability
                temperature=0.1 # Low temperature for deterministic actions
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Brain Freeze (API Error): {e}")
            return None

class Planner:
    def __init__(self):
        try:
            self.client = LLMClient()
        except ValueError as e:
            print(f"Warning: {e}. Brain will not function until key is set.")
            self.client = None

    def decide_next_step(self, user_goal, ui_elements):
        """
        ui_elements: List of dicts [{'text': 'File', 'center': (20,10)}, ...]
        """
        if not self.client:
            return {"action": "error", "thought": "LLM Client not initialized (missing API Key)."}

        # 1. Serialize Visual Context
        context_str = "VISIBLE UI ELEMENTS:\n"
        # Handle if ui_elements is a list of tuples or dicts or strings
        # The vision module returns (log_x, log_y) for a specific find_element call,
        # but here we expect a list of ALL elements.
        # Wait, Phase 2 vision.py only implements 'find_element' which takes a target text.
        # It doesn't have a 'get_all_text_elements' method yet.
        # The plan for Phase 3 assumes we pass a list of elements.
        # For now, we will assume the input 'ui_elements' is passed correctly by the caller,
        # potentially from a future 'scan_all' method in vision.py.
        
        # Let's assume ui_elements is a list of dicts: {'text': '...', 'center': (x, y)}
        for elem in ui_elements:
            text = elem.get('text', 'Unknown')
            # We don't strictly need coordinates in the prompt if we look them up later,
            # but the plan suggests sending them.
            context_str += f"- Text: '{text}'\n"

        # 2. Construct Message History
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"GOAL: {user_goal}\n\n{context_str}"}
        ]

        # 3. Get Decision
        raw_response = self.client.query(messages)
        if not raw_response:
            return {"action": "error", "thought": "No response from LLM."}

        # 4. Parse JSON
        try:
            plan = json.loads(raw_response)
            return plan
        except json.JSONDecodeError:
            return {"action": "error", "thought": "Invalid JSON response from LLM."}

