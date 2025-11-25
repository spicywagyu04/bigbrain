import pyttsx3
import threading

class Voice:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # Select a voice (usually index 0 or 1 for standard OS voices)
            # On macOS, 0 is often Alex, 1 is Fred, etc.
            # self.engine.setProperty('rate', 170) # Speed up slightly
        except Exception as e:
            print(f"Voice init failed: {e}")
            self.engine = None

    def speak(self, text):
        """
        Non-blocking speak function.
        """
        if not self.engine:
            print(f"SILENT MODE (Voice Disabled): {text}")
            return

        def _run():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError:
                 # Loop already running or other engine issues
                 pass

        # Run in separate thread to not block the OODA loop
        threading.Thread(target=_run).start()

