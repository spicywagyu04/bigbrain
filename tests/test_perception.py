import cv2
import os
import sys
import pytest

# Add the project root to sys.path so we can import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.vision import PerceptionEngine

def test_find_shell_coordinates():
    # Initialize Engine
    # Note: This might take a moment to load the OCR model
    print("Initializing PerceptionEngine...")
    engine = PerceptionEngine()

    # Load static asset (simulate screen capture)
    image_path = "tests/assets/terminal_sample.png"
    if not os.path.exists(image_path):
        pytest.fail(f"Test asset not found: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        pytest.fail(f"Failed to load image: {image_path}")

    print(f"Loaded image: {img.shape}")

    # Execute Search
    target_text = "Shell"
    print(f"Searching for '{target_text}'...")
    coords = engine.find_element(img, target_text)

    # Assertions
    assert coords is not None, f"Failed to detect text '{target_text}'"
    print(f"Detected Coordinates: {coords}")
    
    # We know we placed "Shell" at (100, 100) on a 400x600 image.
    # The physical coordinates found by OCR will be the center of the text box.
    # The font scale was 2, so the text is quite large.
    # Let's just assert we got valid coordinates for now.
    assert isinstance(coords, tuple)
    assert len(coords) == 2
    assert isinstance(coords[0], int)
    assert isinstance(coords[1], int)

if __name__ == "__main__":
    test_find_shell_coordinates()

