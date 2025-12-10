"""
Receiver Module
Client that connects to the streaming server and displays the stream
"""

import socket
import threading
import time
import cv2
from decoder import FrameDecoder


class StreamingClient:
    """TCP client that receives and displays the screen stream"""

    def __init__(self, host='127.0.0.1', port=9999):
        """
        Initialize the streaming client

        Args:
            host: Server IP address to connect to
            port: Server port to connect to
        """
        self.host = host
        self.port = port

        self.socket = None
        self.decoder = None

        self.running = False
        self.connected = False

        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()

        # Callbacks for UI updates
        self.on_frame = None
        self.on_status_update = None
        self.on_error = None
        self.on_disconnect = None

    def connect(self):
        """Connect to the streaming server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # Connection timeout
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)  # Remove timeout after connection
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            self.decoder = FrameDecoder()
            self.connected = True
            self.running = True

            # Start receive thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()

            self._notify_status(f"Connected to {self.host}:{self.port}")
            return True

        except socket.timeout:
            self._notify_error("Connection timed out")
            return False
        except ConnectionRefusedError:
            self._notify_error("Connection refused - is the server running?")
            return False
        except Exception as e:
            self._notify_error(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        self.connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        if self.decoder:
            self.decoder.clear()

        self._notify_status("Disconnected")
        if self.on_disconnect:
            self.on_disconnect()

    def _receive_loop(self):
        """Main receive loop - receives and processes frames"""
        while self.running:
            try:
                # Receive data
                data = self.socket.recv(65536)

                if not data:
                    # Connection closed
                    self._notify_status("Server closed connection")
                    self.disconnect()
                    break

                # Add data to decoder
                self.decoder.add_data(data)

                # Try to extract frames
                while True:
                    frame = self.decoder.get_frame()
                    if frame is None:
                        break

                    # Update current frame
                    with self.frame_lock:
                        self.current_frame = frame
                        self.frame_count += 1

                    # Calculate FPS
                    current_time = time.time()
                    if current_time - self.last_fps_time >= 1.0:
                        self.fps = self.frame_count
                        self.frame_count = 0
                        self.last_fps_time = current_time

                    # Notify callback
                    if self.on_frame:
                        self.on_frame(frame)

            except ConnectionResetError:
                self._notify_error("Connection reset by server")
                self.disconnect()
                break
            except Exception as e:
                if self.running:
                    self._notify_error(f"Receive error: {e}")
                    self.disconnect()
                break

    def get_frame(self):
        """Get the current frame"""
        with self.frame_lock:
            return self.current_frame

    def get_fps(self):
        """Get the current FPS"""
        return self.fps

    def is_connected(self):
        """Check if connected"""
        return self.connected

    def _notify_status(self, message):
        """Notify status update"""
        print(f"[CLIENT] {message}")
        if self.on_status_update:
            self.on_status_update(message)

    def _notify_error(self, message):
        """Notify error"""
        print(f"[ERROR] {message}")
        if self.on_error:
            self.on_error(message)


def main():
    """Run the client from command line"""
    import argparse

    parser = argparse.ArgumentParser(description='Screen Streaming Client')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Server IP address')
    parser.add_argument('--port', type=int, default=9999,
                        help='Server port')

    args = parser.parse_args()

    client = StreamingClient(host=args.host, port=args.port)

    print(f"Connecting to {args.host}:{args.port}...")

    if client.connect():
        print("Connected! Press 'q' to quit.")

        try:
            while client.is_connected():
                frame = client.get_frame()
                if frame is not None:
                    # Add FPS overlay
                    fps_text = f"FPS: {client.get_fps()}"
                    cv2.putText(frame, fps_text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    cv2.imshow('Screen Stream', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            pass
        finally:
            client.disconnect()
            cv2.destroyAllWindows()
    else:
        print("Failed to connect")


if __name__ == "__main__":
    main()
