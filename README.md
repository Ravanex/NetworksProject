# Screen Streaming Launcher

A simple LAN screen streaming application that allows you to stream your screen from one laptop to another over a local network.

**Authors:** Randy & Ruben

## Overview

This project provides a real-time screen streaming solution using:
- **Python** - Core programming language
- **Tkinter** - Simple GUI launcher
- **OpenCV** - Frame encoding/decoding
- **Sockets** - TCP network transmission

## Project Structure

```
screen-streaming-launcher/
├── sender/
│   ├── sender.py        # Main streaming server
│   ├── launcher.py      # GUI launcher for sender
│   ├── capture.py       # Screen capture module
│   ├── encoder.py       # Frame compression module
│   └── requirements.txt # Sender dependencies
├── receiver/
│   ├── receiver.py      # Main streaming client
│   ├── launcher.py      # GUI launcher for receiver
│   ├── decoder.py       # Frame decompression module
│   └── requirements.txt # Receiver dependencies
└── README.md            # This file
```

## Requirements

- Python 3.8 or higher
- Both computers must be on the same local network (LAN)

## Installation

### Sender (Streaming PC)

```bash
cd sender
pip install -r requirements.txt
```

### Receiver (Viewing PC)

```bash
cd receiver
pip install -r requirements.txt
```

## Usage

### Quick Start

1. **On the Sender PC (the one sharing its screen):**
   ```bash
   cd sender
   python launcher.py
   ```
   - Note the IP address displayed in the window
   - Click "Start Streaming"

2. **On the Receiver PC (the one viewing the stream):**
   ```bash
   cd receiver
   python launcher.py
   ```
   - Enter the sender's IP address
   - Click "Connect"

### Command Line Usage

You can also run without the GUI:

**Sender:**
```bash
cd sender
python sender.py --port 9999 --quality 50 --fps 30
```

**Receiver:**
```bash
cd receiver
python receiver.py --host <SENDER_IP> --port 9999
```

## Configuration Options

### Sender Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Port | TCP port to listen on | 9999 |
| Quality | JPEG compression (1-100) | 50 |
| FPS | Target frames per second | 30 |
| Scale | Frame size multiplier | 1.0 |

### Receiver Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Host | Sender's IP address | 127.0.0.1 |
| Port | TCP port to connect to | 9999 |
| Display Mode | embedded/window/fullscreen | embedded |

## Display Modes (Receiver)

- **Embedded Preview**: Shows stream in the launcher window
- **Separate Window**: Opens a resizable OpenCV window
- **Fullscreen**: Opens in fullscreen mode (press ESC or Q to exit)

## Troubleshooting

### Connection Issues

1. **"Connection refused"**
   - Make sure the sender is running and "Start Streaming" was clicked
   - Check that you're using the correct IP address
   - Verify both computers are on the same network

2. **"Connection timed out"**
   - Check firewall settings - allow Python through the firewall
   - Verify the port (9999) is not blocked

3. **Laggy stream**
   - Lower the quality setting on the sender
   - Reduce the FPS
   - Use a smaller scale (0.5 or 0.75)

### Finding Your IP Address

- **Windows**: Open CMD and type `ipconfig`
- **macOS/Linux**: Open Terminal and type `ifconfig` or `ip addr`

Look for the IPv4 address starting with `192.168.x.x` or `10.x.x.x`

## Technical Details

### How It Works

1. **Capture**: The sender captures the screen using the `mss` library
2. **Encode**: Frames are compressed using JPEG encoding via OpenCV
3. **Transmit**: Compressed frames are sent over TCP with a size header
4. **Decode**: The receiver decompresses the JPEG data
5. **Display**: Frames are displayed using OpenCV or Tkinter

### Network Protocol

- Uses TCP for reliable transmission
- Each frame is prefixed with a 4-byte size header (big-endian)
- Frame data is JPEG-encoded for compression

## License

This project was created for educational purposes demonstrating networking, real-time transmission, and socket programming concepts.
