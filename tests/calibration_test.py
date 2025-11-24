from core.retina import get_scale_factor, to_logical
from core.motor import Hand
import time

def test_calibration():
    print("Starting Calibration Test...")
    
    # 1. Get Scale Factor
    scale = get_scale_factor()
    print(f"Detected Scale Factor: {scale}")
    
    # 2. Initialize Hand
    hand = Hand()
    
    # Example: On a 2x Retina, Logical (100, 100) is Physical (200, 200).
    # We use a safe arbitrary point for the test.
    physical_x = 200
    physical_y = 200
    
    logical_x, logical_y = to_logical(physical_x, physical_y, scale)
    print(f"Physical ({physical_x}, {physical_y}) -> Logical ({logical_x}, {logical_y})")
    
    print("Moving mouse to calculated coordinates in 2 seconds...")
    time.sleep(2)
    hand.move_to(logical_x, logical_y)
    print("Movement complete.")

if __name__ == "__main__":
    test_calibration()

