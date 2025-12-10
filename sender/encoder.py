"""
Frame Encoder Module
Compresses frames for efficient transmission over the network
"""

import cv2
import struct


class FrameEncoder:
    """Handles frame compression and encoding for network transmission"""

    def __init__(self, quality=50, scale=1.0):
        """
        Initialize the encoder

        Args:
            quality: JPEG compression quality (0-100, higher = better quality, larger size)
            scale: Scale factor for resizing frames (0.5 = half size)
        """
        self.quality = quality
        self.scale = scale

    def encode(self, frame):
        """
        Encode a frame for transmission

        Args:
            frame: numpy.ndarray in BGR format

        Returns:
            bytes: Encoded frame data with size header
        """
        # Resize if scale is not 1.0
        if self.scale != 1.0:
            width = int(frame.shape[1] * self.scale)
            height = int(frame.shape[0] * self.scale)
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

        # Encode as JPEG
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.quality]
        _, encoded = cv2.imencode('.jpg', frame, encode_params)

        # Convert to bytes
        data = encoded.tobytes()

        # Prepend the size of the data (4 bytes, big-endian)
        size = len(data)
        header = struct.pack('>I', size)

        return header + data

    def set_quality(self, quality):
        """Update the compression quality"""
        self.quality = max(1, min(100, quality))

    def set_scale(self, scale):
        """Update the scale factor"""
        self.scale = max(0.1, min(1.0, scale))


def test_encoder():
    """Test the encoder functionality"""
    import numpy as np

    # Create a test frame
    frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    print(f"Original frame size: {frame.nbytes} bytes")

    encoder = FrameEncoder(quality=50)
    encoded = encoder.encode(frame)
    print(f"Encoded size: {len(encoded)} bytes")
    print(f"Compression ratio: {frame.nbytes / len(encoded):.2f}x")


if __name__ == "__main__":
    test_encoder()
