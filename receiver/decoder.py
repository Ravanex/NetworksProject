"""
Frame Decoder Module
Decompresses frames received from the network
"""

import cv2
import numpy as np
import struct


class FrameDecoder:
    """Handles frame decompression and decoding from network data"""

    def __init__(self):
        """Initialize the decoder"""
        self.buffer = b''

    def add_data(self, data):
        """
        Add received data to the buffer

        Args:
            data: Raw bytes received from the network
        """
        self.buffer += data

    def get_frame(self):
        """
        Try to extract a complete frame from the buffer

        Returns:
            numpy.ndarray or None: Decoded frame in BGR format, or None if incomplete
        """
        # Need at least 4 bytes for the size header
        if len(self.buffer) < 4:
            return None

        # Read the frame size
        frame_size = struct.unpack('>I', self.buffer[:4])[0]

        # Check if we have the complete frame
        if len(self.buffer) < 4 + frame_size:
            return None

        # Extract the frame data
        frame_data = self.buffer[4:4 + frame_size]

        # Remove processed data from buffer
        self.buffer = self.buffer[4 + frame_size:]

        # Decode the JPEG frame
        try:
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            print(f"Decode error: {e}")
            return None

    def clear(self):
        """Clear the buffer"""
        self.buffer = b''

    def buffer_size(self):
        """Get current buffer size"""
        return len(self.buffer)


def test_decoder():
    """Test the decoder functionality"""
    # Create a test frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Encode it
    _, encoded = cv2.imencode('.jpg', test_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
    data = encoded.tobytes()
    header = struct.pack('>I', len(data))

    # Test decoder
    decoder = FrameDecoder()
    decoder.add_data(header + data)

    frame = decoder.get_frame()
    if frame is not None:
        print(f"Successfully decoded frame: {frame.shape}")
    else:
        print("Failed to decode frame")


if __name__ == "__main__":
    test_decoder()
