import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    def __init__(self):
        # Initialize the client with the API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fallback or error logging, but we'll raise to be safe
            # In production, we might want to handle this more gracefully
            pass 
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Using GPT-4o as requested/standard
        
    def query(self, messages, tools=None, tool_choice=None):
        """
        Sends a structured conversation to the LLM and returns the response.
        Supports Function Calling (Tools) if provided.
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1 # Low temperature for deterministic actions
            }
            
            if tools:
                params["tools"] = tools
                params["tool_choice"] = tool_choice
            else:
                 # Use JSON mode only if NO tools are provided
                 # Mixing tools and response_format can sometimes be tricky depending on API version,
                 # but generally we use tools OR json_object.
                 params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**params)
            
            if tools and response.choices[0].message.tool_calls:
                return response.choices[0].message.tool_calls[0].function.arguments
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Brain Freeze (API Error): {e}")
            return None

class Planner:
    def __init__(self):
        try:
            self.client = LLMClient()
        except Exception as e:
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
        for elem in ui_elements:
            text = elem.get('text', 'Unknown')
            context_str += f"- Text: '{text}'\n"

        # 2. Construct Message History
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"GOAL: {user_goal}\n\n{context_str}"}
        ]
        
        # 3. Define Tools (Function Calling)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_action",
                    "description": "Execute a desktop automation action based on the user goal and screen state.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "thought": {
                                "type": "string",
                                "description": "Brief reasoning about what to click and why."
                            },
                            "action": {
                                "type": "string",
                                "enum": ["click", "type", "scroll", "done", "fail", "error"],
                                "description": "The action to perform."
                            },
                            "target_text": {
                                "type": "string",
                                "description": "The exact text from the screen elements list to click (required for 'click' action)."
                            },
                            "text_to_type": {
                                "type": "string",
                                "description": "The text to type (required for 'type' action)."
                            }
                        },
                        "required": ["thought", "action"]
                    }
                }
            }
        ]

        # 4. Get Decision via Tool Call
        raw_response = self.client.query(
            messages, 
            tools=tools, 
            tool_choice={"type": "function", "function": {"name": "execute_action"}}
        )
        
        if not raw_response:
            return {"action": "error", "thought": "No response from LLM."}

        # 5. Parse JSON (Tool arguments are always JSON strings)
        try:
            plan = json.loads(raw_response)
            return plan
        except json.JSONDecodeError:
            return {"action": "error", "thought": "Invalid JSON response from LLM Tool Call."}
