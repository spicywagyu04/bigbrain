import unittest
from unittest.mock import MagicMock, patch
from core.brain import Planner

class TestBrain(unittest.TestCase):
    
    @patch('core.brain.LLMClient')
    def test_planner_decision(self, MockLLMClient):
        # 1. Setup Mock
        # Create a mock instance of LLMClient
        mock_client_instance = MockLLMClient.return_value
        
        # Mock the query method to return a valid JSON string
        mock_response = '{"thought": "The user wants to save. I see a Save button.", "action": "click", "target_text": "Save"}'
        mock_client_instance.query.return_value = mock_response
        
        # 2. Initialize Planner
        # The Planner will use the mock client because we patched the class
        planner = Planner()
        
        # 3. Define Mock UI Context
        fake_ui = [
            {"text": "File", "center": (100, 20)},
            {"text": "Edit", "center": (150, 20)},
            {"text": "Save", "center": (100, 50)}
        ]
        
        # 4. Execute Decision
        user_goal = "Click the Save button"
        plan = planner.decide_next_step(user_goal, fake_ui)
        
        # 5. Assertions
        print(f"\nPlanner Output: {plan}")
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan['action'], 'click')
        self.assertEqual(plan['target_text'], 'Save')
        self.assertIn("user wants to save", plan['thought'])

if __name__ == '__main__':
    unittest.main()

