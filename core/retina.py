import Quartz
from AppKit import NSScreen

def get_scale_factor():
    """
    Dynamically fetches the backingScaleFactor of the main screen.
    Returns: float (usually 2.0 for Retina, 1.0 for standard)
    """
    screen = NSScreen.mainScreen()
    scale = screen.backingScaleFactor()
    return scale

def to_logical(physical_x, physical_y, scale_factor):
    """
    Converts OCR coordinates (physical) to Mouse coordinates (logical).
    """
    return int(physical_x / scale_factor), int(physical_y / scale_factor)

