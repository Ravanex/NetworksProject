"""
Sender Launcher
Simple Tkinter GUI for the screen streaming server
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from sender import StreamingServer


class SenderLauncher:
    """GUI Launcher for the Screen Streaming Server"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Streamer - Sender")
        self.root.geometry("400x580")
        self.root.resizable(True, True)
        self.root.minsize(380, 500)

        self.server = None
        self.is_streaming = False

        self._create_widgets()
        self._update_ip_display()

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Screen Streamer",
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 5))

        subtitle_label = ttk.Label(main_frame, text="Sender / Host",
                                   font=('Helvetica', 12))
        subtitle_label.pack(pady=(0, 10))

        # IP Display Frame
        ip_frame = ttk.LabelFrame(main_frame, text="Connection Info", padding="10")
        ip_frame.pack(fill=tk.X, pady=(0, 10))

        self.ip_label = ttk.Label(ip_frame, text="IP: Loading...",
                                  font=('Courier', 11))
        self.ip_label.pack()

        self.port_display = ttk.Label(ip_frame, text="Port: 9999",
                                      font=('Courier', 11))
        self.port_display.pack()

        # START STREAMING BUTTON - Prominent placement
        self.start_btn = ttk.Button(main_frame, text="Start Streaming",
                                    command=self._toggle_streaming)
        self.start_btn.pack(fill=tk.X, pady=10, ipady=8)

        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Not streaming",
                                      font=('Helvetica', 10))
        self.status_label.pack()

        self.clients_label = ttk.Label(status_frame, text="Clients: 0",
                                       font=('Helvetica', 10))
        self.clients_label.pack()

        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Port setting
        port_row = ttk.Frame(settings_frame)
        port_row.pack(fill=tk.X, pady=2)
        ttk.Label(port_row, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="9999")
        self.port_entry = ttk.Entry(port_row, textvariable=self.port_var, width=10)
        self.port_entry.pack(side=tk.RIGHT)

        # Quality setting
        quality_row = ttk.Frame(settings_frame)
        quality_row.pack(fill=tk.X, pady=2)
        ttk.Label(quality_row, text="Quality:").pack(side=tk.LEFT)
        self.quality_var = tk.IntVar(value=75)
        self.quality_scale = ttk.Scale(quality_row, from_=10, to=100,
                                       variable=self.quality_var, orient=tk.HORIZONTAL)
        self.quality_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        quality_val_row = ttk.Frame(settings_frame)
        quality_val_row.pack(fill=tk.X)
        self.quality_label = ttk.Label(quality_val_row, text="75%")
        self.quality_label.pack(side=tk.RIGHT)
        self.quality_var.trace('w', self._update_quality_label)

        # FPS setting
        fps_row = ttk.Frame(settings_frame)
        fps_row.pack(fill=tk.X, pady=2)
        ttk.Label(fps_row, text="FPS:").pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=30)
        self.fps_scale = ttk.Scale(fps_row, from_=5, to=60,
                                   variable=self.fps_var, orient=tk.HORIZONTAL)
        self.fps_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        fps_val_row = ttk.Frame(settings_frame)
        fps_val_row.pack(fill=tk.X)
        self.fps_label = ttk.Label(fps_val_row, text="30 FPS")
        self.fps_label.pack(side=tk.RIGHT)
        self.fps_var.trace('w', self._update_fps_label)

        # Scale setting
        scale_row = ttk.Frame(settings_frame)
        scale_row.pack(fill=tk.X, pady=2)
        ttk.Label(scale_row, text="Scale:").pack(side=tk.LEFT)
        self.scale_var = tk.DoubleVar(value=1.0)
        self.scale_combo = ttk.Combobox(scale_row, textvariable=self.scale_var,
                                        values=[0.25, 0.5, 0.75, 1.0], width=8, state='readonly')
        self.scale_combo.pack(side=tk.RIGHT)
        self.scale_combo.set(1.0)

        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=5, width=40, state=tk.DISABLED,
                                font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL,
                                  command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _update_quality_label(self, *args):
        """Update quality label when slider changes"""
        self.quality_label.config(text=f"{self.quality_var.get()}%")
        if self.server and self.is_streaming:
            self.server.set_quality(self.quality_var.get())

    def _update_fps_label(self, *args):
        """Update FPS label when slider changes"""
        self.fps_label.config(text=f"{self.fps_var.get()} FPS")
        if self.server and self.is_streaming:
            self.server.set_fps(self.fps_var.get())

    def _update_ip_display(self):
        """Update the IP address display"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"

        self.ip_label.config(text=f"IP: {ip}")

    def _toggle_streaming(self):
        """Start or stop streaming"""
        if not self.is_streaming:
            self._start_streaming()
        else:
            self._stop_streaming()

    def _start_streaming(self):
        """Start the streaming server"""
        try:
            port = int(self.port_var.get())
            quality = self.quality_var.get()
            fps = self.fps_var.get()
            scale = float(self.scale_var.get())

            self.server = StreamingServer(
                port=port,
                quality=quality,
                fps=fps,
                scale=scale
            )

            # Set callbacks
            self.server.on_status_update = self._log_message
            self.server.on_error = self._log_error
            self.server.on_client_connect = lambda addr: self._update_clients()
            self.server.on_client_disconnect = self._update_clients

            if self.server.start():
                self.is_streaming = True
                self.start_btn.config(text="Stop Streaming")
                self.status_label.config(text="Streaming...")
                self.port_display.config(text=f"Port: {port}")
                self.port_entry.config(state='disabled')
                self.scale_combo.config(state='disabled')
                self._log_message("Streaming started")
                self._start_client_counter()
            else:
                messagebox.showerror("Error", "Failed to start server")

        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {e}")

    def _stop_streaming(self):
        """Stop the streaming server"""
        if self.server:
            self.server.stop()
            self.server = None

        self.is_streaming = False
        self.start_btn.config(text="Start Streaming")
        self.status_label.config(text="Not streaming")
        self.clients_label.config(text="Clients: 0")
        self.port_entry.config(state='normal')
        self.scale_combo.config(state='readonly')
        self._log_message("Streaming stopped")

    def _update_clients(self, *args):
        """Update the client count display"""
        if self.server:
            count = self.server.get_client_count()
            self.clients_label.config(text=f"Clients: {count}")

    def _start_client_counter(self):
        """Start periodic client count updates"""
        if self.is_streaming:
            self._update_clients()
            self.root.after(1000, self._start_client_counter)

    def _log_message(self, message):
        """Add a message to the log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_error(self, message):
        """Add an error message to the log"""
        self._log_message(f"[ERROR] {message}")

    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        """Handle window close"""
        if self.is_streaming:
            self._stop_streaming()
        self.root.destroy()


def main():
    """Main entry point"""
    app = SenderLauncher()
    app.run()


if __name__ == "__main__":
    main()
