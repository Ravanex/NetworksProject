"""
Screen Capture Module
Captures the screen using mss (cross-platform screen capture library)
"""

import numpy as np
import threading

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ScreenCapture:
    """Handles screen capture functionality - thread-safe"""

    def __init__(self, monitor_number=1):
        """
        Initialize the screen capture

        Args:
            monitor_number: Which monitor to capture (1 = primary)
        """
        self.monitor_number = monitor_number
        self._local = threading.local()

        if MSS_AVAILABLE:
            self.capture_method = "mss"
        elif PIL_AVAILABLE:
            self.capture_method = "pil"
        else:
            raise ImportError("Neither mss nor PIL is available for screen capture")

    def _get_mss(self):
        """Get thread-local mss instance"""
        if not hasattr(self._local, 'sct') or self._local.sct is None:
            self._local.sct = mss.mss()
        return self._local.sct

    def get_monitors(self):
        """Get list of available monitors"""
        if self.capture_method == "mss":
            return self._get_mss().monitors
        return [{"left": 0, "top": 0, "width": 1920, "height": 1080}]

    def capture_frame(self):
        """
        Capture a single frame from the screen

        Returns:
            numpy.ndarray: The captured frame in BGR format (OpenCV compatible)
        """
        if self.capture_method == "mss":
            return self._capture_mss()
        else:
            return self._capture_pil()

    def _capture_mss(self):
        """Capture using mss library"""
        sct = self._get_mss()
        monitors = sct.monitors

        # Select monitor (0 = all monitors, 1+ = specific monitor)
        if self.monitor_number < len(monitors):
            monitor = monitors[self.monitor_number]
        else:
            monitor = monitors[1]  # Default to primary

        # Capture the screen
        screenshot = sct.grab(monitor)

        # Convert to numpy array (BGRA format)
        frame = np.array(screenshot)

        # Convert BGRA to BGR (remove alpha channel)
        frame = frame[:, :, :3]

        return frame

    def _capture_pil(self):
        """Capture using PIL (Windows/macOS fallback)"""
        screenshot = ImageGrab.grab()
        frame = np.array(screenshot)

        # PIL captures in RGB, convert to BGR for OpenCV
        frame = frame[:, :, ::-1]

        return frame

    def get_screen_size(self):
        """Get the size of the capture area"""
        if self.capture_method == "mss":
            sct = self._get_mss()
            monitors = sct.monitors
            if self.monitor_number < len(monitors):
                monitor = monitors[self.monitor_number]
            else:
                monitor = monitors[1]
            return (monitor["width"], monitor["height"])
        return (1920, 1080)  # Default fallback

    def close(self):
        """Clean up resources"""
        if hasattr(self._local, 'sct') and self._local.sct:
            self._local.sct.close()
            self._local.sct = None


def test_capture():
    """Test the screen capture functionality"""
    import cv2

    capture = ScreenCapture()
    print(f"Using capture method: {capture.capture_method}")
    print(f"Screen size: {capture.get_screen_size()}")

    frame = capture.capture_frame()
    print(f"Captured frame shape: {frame.shape}")

    # Save a test image
    cv2.imwrite("test_capture.png", frame)
    print("Saved test_capture.png")

    capture.close()


if __name__ == "__main__":
    test_capture()
