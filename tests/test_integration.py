import unittest
from unittest.mock import MagicMock, patch
import json
from main import OmniAgent

class TestIntegration(unittest.TestCase):

    @patch('core.brain.LLMClient')
    @patch('main.Eye')
    @patch('main.Hand')
    @patch('main.Voice')
    def test_full_loop_mock(self, MockVoice, MockHand, MockEye, MockLLMClient):
        """
        Simulates one full iteration of the Agent Loop without using real API or Screen.
        """
        # 1. Setup Mocks
        # Brain Mock
        mock_llm = MockLLMClient.return_value
        # Simulate Tool Call response (which comes back as a JSON string of arguments)
        mock_llm.query.return_value = json.dumps({
            "thought": "I see the File menu. I will click it.",
            "action": "click",
            "target_text": "File"
        })

        # Vision Mock (The Eye)
        mock_eye = MockEye.return_value
        # Return a dummy image (doesn't matter content as we mock OCR next)
        mock_eye.capture.return_value = "dummy_image_array"

        # Vision Mock (The OCR Engine inside Perception)
        with patch('core.vision.PerceptionEngine.scan_full') as mock_scan:
            mock_scan.return_value = [
                {'text': 'File', 'center': (100, 20)},
                {'text': 'Edit', 'center': (200, 20)}
            ]

            # Motor Mock
            mock_hand = MockHand.return_value
            
            # Voice Mock
            mock_voice = MockVoice.return_value

            # 2. Initialize Agent
            agent = OmniAgent()

            # 3. Inject Mocks (Constructor already created real objects, we swap them)
            
            # 4. Run a single "step" of the loop manually
            
            # Step A: Observe
            screenshot = agent.eye.capture()
            ui_elements = agent.perception.scan_full(screenshot)
            
            # Step B: Decide
            user_goal = "Open File Menu"
            plan = agent.brain.decide_next_step(user_goal, ui_elements)
            
            # Step C: Act
            agent.execute_plan(plan, ui_elements, screenshot)

            # 5. Assertions
            # Did we ask the brain?
            mock_llm.query.assert_called_once()
            
            # Did we click the right coordinates?
            # 'File' is at (100, 20) in our mock_scan return value
            mock_hand.click.assert_called_with(100, 20)
            
            print("\nIntegration Test Passed: Agent observed 'File' and clicked (100, 20).")

if __name__ == '__main__':
    unittest.main()
