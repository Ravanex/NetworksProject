"""
Receiver Launcher
Simple Tkinter GUI for the screen streaming client/viewer
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
from PIL import Image, ImageTk
from receiver import StreamingClient


class ReceiverLauncher:
    """GUI Launcher for the Screen Streaming Viewer"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Streamer - Viewer")
        self.root.geometry("450x600")
        self.root.resizable(True, True)
        self.root.minsize(400, 500)

        self.client = None
        self.is_connected = False
        self.display_window = None

        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Screen Streamer",
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 10))

        subtitle_label = ttk.Label(main_frame, text="Viewer / Receiver",
                                   font=('Helvetica', 12))
        subtitle_label.pack(pady=(0, 20))

        # Connection Frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        # Host input
        host_row = ttk.Frame(conn_frame)
        host_row.pack(fill=tk.X, pady=2)
        ttk.Label(host_row, text="Host IP:").pack(side=tk.LEFT)
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.host_entry = ttk.Entry(host_row, textvariable=self.host_var, width=20)
        self.host_entry.pack(side=tk.RIGHT)

        # Port input
        port_row = ttk.Frame(conn_frame)
        port_row.pack(fill=tk.X, pady=2)
        ttk.Label(port_row, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="9999")
        self.port_entry = ttk.Entry(port_row, textvariable=self.port_var, width=20)
        self.port_entry.pack(side=tk.RIGHT)

        # Display Options Frame
        display_frame = ttk.LabelFrame(main_frame, text="Display Options", padding="10")
        display_frame.pack(fill=tk.X, pady=(0, 10))

        # Display mode
        self.display_mode = tk.StringVar(value="embedded")
        ttk.Radiobutton(display_frame, text="Embedded Preview",
                        variable=self.display_mode, value="embedded").pack(anchor=tk.W)
        ttk.Radiobutton(display_frame, text="Separate Window",
                        variable=self.display_mode, value="window").pack(anchor=tk.W)
        ttk.Radiobutton(display_frame, text="Fullscreen",
                        variable=self.display_mode, value="fullscreen").pack(anchor=tk.W)

        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Not connected",
                                      font=('Helvetica', 10))
        self.status_label.pack()

        self.fps_label = ttk.Label(status_frame, text="FPS: --",
                                   font=('Helvetica', 10))
        self.fps_label.pack()

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.connect_btn = ttk.Button(button_frame, text="Connect",
                                      command=self._toggle_connection)
        self.connect_btn.pack(fill=tk.X, pady=2)

        # Preview Frame
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_label = ttk.Label(preview_frame, text="No stream",
                                       anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.X, pady=(10, 0))

        self.log_text = tk.Text(log_frame, height=4, width=40, state=tk.DISABLED,
                                font=('Courier', 9))
        self.log_text.pack(fill=tk.X)

        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL,
                                  command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _toggle_connection(self):
        """Connect or disconnect"""
        if not self.is_connected:
            self._connect()
        else:
            self._disconnect()

    def _connect(self):
        """Connect to the streaming server"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())

            if not host:
                messagebox.showerror("Error", "Please enter a host IP address")
                return

            self.client = StreamingClient(host=host, port=port)

            # Set callbacks
            self.client.on_status_update = self._log_message
            self.client.on_error = self._log_error
            self.client.on_disconnect = self._on_disconnect

            # Connect in a thread to avoid blocking UI
            self.connect_btn.config(state='disabled')
            self.status_label.config(text="Connecting...")

            def connect_thread():
                if self.client.connect():
                    self.root.after(0, self._on_connected)
                else:
                    self.root.after(0, self._on_connect_failed)

            threading.Thread(target=connect_thread, daemon=True).start()

        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def _on_connected(self):
        """Called when connection is successful"""
        self.is_connected = True
        self.connect_btn.config(text="Disconnect", state='normal')
        self.status_label.config(text="Connected")
        self.host_entry.config(state='disabled')
        self.port_entry.config(state='disabled')

        # Start display based on mode
        mode = self.display_mode.get()
        if mode == "embedded":
            self._start_embedded_display()
        elif mode == "window":
            self._start_window_display()
        else:  # fullscreen
            self._start_fullscreen_display()

        self._start_fps_counter()

    def _on_connect_failed(self):
        """Called when connection fails"""
        self.connect_btn.config(state='normal')
        self.status_label.config(text="Connection failed")

    def _on_disconnect(self):
        """Called when disconnected"""
        self.root.after(0, self._handle_disconnect)

    def _handle_disconnect(self):
        """Handle disconnect on main thread"""
        self.is_connected = False
        self.connect_btn.config(text="Connect", state='normal')
        self.status_label.config(text="Disconnected")
        self.fps_label.config(text="FPS: --")
        self.host_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self.preview_label.config(image='', text="No stream")

        if self.display_window:
            try:
                cv2.destroyWindow('Screen Stream')
            except:
                pass
            self.display_window = None

    def _disconnect(self):
        """Disconnect from the server"""
        if self.client:
            self.client.disconnect()
            self.client = None

    def _start_embedded_display(self):
        """Start displaying stream in embedded preview"""
        def update_preview():
            if not self.is_connected or not self.client:
                return

            frame = self.client.get_frame()
            if frame is not None:
                # Resize frame to fit preview
                preview_width = self.preview_label.winfo_width()
                preview_height = self.preview_label.winfo_height()

                if preview_width > 1 and preview_height > 1:
                    # Calculate aspect ratio
                    h, w = frame.shape[:2]
                    aspect = w / h

                    if preview_width / preview_height > aspect:
                        new_height = preview_height
                        new_width = int(preview_height * aspect)
                    else:
                        new_width = preview_width
                        new_height = int(preview_width / aspect)

                    frame = cv2.resize(frame, (new_width, new_height))

                # Convert to PhotoImage
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=img)

                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo

            if self.is_connected:
                self.root.after(33, update_preview)  # ~30 FPS

        self.root.after(100, update_preview)

    def _start_window_display(self):
        """Start displaying stream in separate OpenCV window"""
        self.display_window = True

        def display_thread():
            window_name = 'Screen Stream'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            while self.is_connected and self.client:
                # Check if window was closed with X button
                try:
                    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                        self.root.after(0, self._disconnect)
                        break
                except cv2.error:
                    self.root.after(0, self._disconnect)
                    break

                frame = self.client.get_frame()
                if frame is not None:
                    # Add FPS overlay
                    fps_text = f"FPS: {self.client.get_fps()}"
                    cv2.putText(frame, fps_text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    try:
                        cv2.imshow(window_name, frame)
                    except cv2.error:
                        break

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.root.after(0, self._disconnect)
                    break

            try:
                cv2.destroyAllWindows()
            except:
                pass

        threading.Thread(target=display_thread, daemon=True).start()

    def _start_fullscreen_display(self):
        """Start displaying stream in fullscreen"""
        self.display_window = True

        def display_thread():
            window_name = 'Screen Stream'
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_FULLSCREEN)

            while self.is_connected and self.client:
                # Check if window was closed
                try:
                    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                        self.root.after(0, self._disconnect)
                        break
                except cv2.error:
                    self.root.after(0, self._disconnect)
                    break

                frame = self.client.get_frame()
                if frame is not None:
                    try:
                        cv2.imshow(window_name, frame)
                    except cv2.error:
                        break

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # q or ESC
                    self.root.after(0, self._disconnect)
                    break

            try:
                cv2.destroyAllWindows()
            except:
                pass

        threading.Thread(target=display_thread, daemon=True).start()

    def _start_fps_counter(self):
        """Start periodic FPS updates"""
        if self.is_connected and self.client:
            self.fps_label.config(text=f"FPS: {self.client.get_fps()}")
            self.root.after(500, self._start_fps_counter)

    def _log_message(self, message):
        """Add a message to the log"""
        def update():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        self.root.after(0, update)

    def _log_error(self, message):
        """Add an error message to the log"""
        self._log_message(f"[ERROR] {message}")

    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        """Handle window close"""
        if self.is_connected:
            self._disconnect()
        self.root.destroy()


def main():
    """Main entry point"""
    app = ReceiverLauncher()
    app.run()


if __name__ == "__main__":
    main()
