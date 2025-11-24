import cv2
import numpy as np

def create_test_image():
    # Create a white image
    height, width = 400, 600
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add text "Shell"
    # Coordinates: around (100, 100)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, 'Shell', (100, 100), font, 2, (0, 0, 0), 3, cv2.LINE_AA)
    
    # Save it
    cv2.imwrite('tests/assets/terminal_sample.png', image)
    print("Created tests/assets/terminal_sample.png")

if __name__ == "__main__":
    create_test_image()

