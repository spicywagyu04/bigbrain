import pyautogui

class Hand:
    def __init__(self):
        # FAILSAFE: Dragging mouse to any corner throws FailSafeException
        pyautogui.FAILSAFE = True 
        # PAUSE: Add 0.1s delay after every action for stability
        pyautogui.PAUSE = 0.1 

    def move_to(self, x, y):
        """
        Moves mouse to logical coordinates (x, y).
        """
        try:
            pyautogui.moveTo(x, y)
        except pyautogui.FailSafeException:
            print("🚨 FAILSAFE TRIGGERED. ABORTING AGENT.")
            exit(1)

    def click(self, x, y):
        self.move_to(x, y)
        pyautogui.click()

    def type_text(self, text):
        """
        Types the given text string.
        """
        try:
            # typewrite is the standard function in older pyautogui versions, 
            # but write is preferred in newer ones. Let's stick to write.
            pyautogui.write(text, interval=0.05) 
        except pyautogui.FailSafeException:
            print("🚨 FAILSAFE TRIGGERED. ABORTING AGENT.")
            exit(1)
