"""
Sender Module
Main streaming server that captures screen and sends to connected clients
"""

import socket
import threading
import time
from capture import ScreenCapture
from encoder import FrameEncoder


class StreamingServer:
    """TCP server that streams screen capture to connected clients"""

    def __init__(self, host='0.0.0.0', port=9999, quality=50, fps=30, scale=1.0):
        """
        Initialize the streaming server

        Args:
            host: IP address to bind to (0.0.0.0 for all interfaces)
            port: Port to listen on
            quality: JPEG compression quality (1-100)
            fps: Target frames per second
            scale: Scale factor for frame size
        """
        self.host = host
        self.port = port
        self.fps = fps
        self.quality = quality
        self.scale = scale

        self.server_socket = None
        self.capture = None
        self.encoder = None

        self.running = False
        self.clients = []
        self.clients_lock = threading.Lock()

        # Callbacks for UI updates
        self.on_client_connect = None
        self.on_client_disconnect = None
        self.on_status_update = None
        self.on_error = None

    def start(self):
        """Start the streaming server"""
        try:
            # Initialize capture and encoder
            self.capture = ScreenCapture()
            self.encoder = FrameEncoder(quality=self.quality, scale=self.scale)

            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Allow checking for stop

            self.running = True

            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
            accept_thread.start()

            # Start streaming thread
            stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
            stream_thread.start()

            self._notify_status(f"Server started on {self.host}:{self.port}")
            return True

        except Exception as e:
            self._notify_error(f"Failed to start server: {e}")
            return False

    def stop(self):
        """Stop the streaming server"""
        self.running = False

        # Close all client connections
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # Close capture
        if self.capture:
            self.capture.close()

        self._notify_status("Server stopped")

    def _accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                with self.clients_lock:
                    self.clients.append(client_socket)

                self._notify_status(f"Client connected: {address}")
                if self.on_client_connect:
                    self.on_client_connect(address)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self._notify_error(f"Accept error: {e}")

    def _stream_loop(self):
        """Main streaming loop - captures and sends frames"""
        while self.running:
            start_time = time.time()

            try:
                # Capture frame
                frame = self.capture.capture_frame()

                # Encode frame
                encoded_data = self.encoder.encode(frame)

                # Send to all connected clients
                self._broadcast(encoded_data)

            except Exception as e:
                self._notify_error(f"Stream error: {e}")

            # Maintain target FPS (recalculate each loop so changes take effect)
            elapsed = time.time() - start_time
            frame_time = 1.0 / self.fps
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _broadcast(self, data):
        """Send data to all connected clients"""
        disconnected = []
        disconnect_count = 0

        with self.clients_lock:
            for client in self.clients:
                try:
                    client.sendall(data)
                except Exception:
                    disconnected.append(client)

            # Remove disconnected clients
            for client in disconnected:
                self.clients.remove(client)
                try:
                    client.close()
                except:
                    pass
                disconnect_count += 1

        # Notify outside the lock to avoid deadlock
        for _ in range(disconnect_count):
            self._notify_status("Client disconnected")
            if self.on_client_disconnect:
                try:
                    self.on_client_disconnect()
                except Exception:
                    pass

    def get_client_count(self):
        """Get the number of connected clients"""
        with self.clients_lock:
            return len(self.clients)

    def set_quality(self, quality):
        """Update streaming quality"""
        self.quality = quality
        if self.encoder:
            self.encoder.set_quality(quality)

    def set_fps(self, fps):
        """Update target FPS"""
        self.fps = max(1, min(60, fps))

    def set_scale(self, scale):
        """Update frame scale"""
        self.scale = scale
        if self.encoder:
            self.encoder.set_scale(scale)

    def _notify_status(self, message):
        """Notify status update"""
        print(f"[SERVER] {message}")
        if self.on_status_update:
            self.on_status_update(message)

    def _notify_error(self, message):
        """Notify error"""
        print(f"[ERROR] {message}")
        if self.on_error:
            self.on_error(message)

    def get_local_ip(self):
        """Get the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


def main():
    """Run the server from command line"""
    import argparse

    parser = argparse.ArgumentParser(description='Screen Streaming Server')
    parser.add_argument('--port', type=int, default=9999, help='Port to listen on')
    parser.add_argument('--quality', type=int, default=50, help='JPEG quality (1-100)')
    parser.add_argument('--fps', type=int, default=30, help='Target FPS')
    parser.add_argument('--scale', type=float, default=1.0, help='Scale factor (0.1-1.0)')

    args = parser.parse_args()

    server = StreamingServer(
        port=args.port,
        quality=args.quality,
        fps=args.fps,
        scale=args.scale
    )

    print(f"Starting server...")
    print(f"Local IP: {server.get_local_ip()}")

    if server.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.stop()


if __name__ == "__main__":
    main()
