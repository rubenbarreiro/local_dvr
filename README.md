# local_dvr

A simple DVR for local RTSP streams from WiFi cameras. Provides live viewing and recording functionality.

## Prerequisites (Ubuntu/Debian-based systems)

Before installing, ensure you have the following system dependencies:

- **FFmpeg**: Required for RTSP stream handling, probing, and recording (`ffmpeg` and `ffprobe`)
- **Python 3.8+**: Tested with Python 3.14
- **python3-venv**: Required for creating isolated Python virtual environments

## Installation

### 1. Update package lists

```bash
sudo apt update
```

### 2. Install system dependencies

Install FFmpeg and Python venv support:

```bash
sudo apt install -y ffmpeg python3-venv
```

Verify FFmpeg installation:

```bash
ffmpeg -version && ffprobe -version
```

### 3. Set up a Python virtual environment (recommended)

Ubuntu uses PEP 668 (externally managed Python), so it's strongly recommended to use an isolated virtual environment:

```bash
cd /home/ruben/Projects/local_dvr
python3 -m venv .venv
source .venv/bin/activate
```

Your shell prompt should now show `(.venv)` indicating the environment is active. To deactivate later:

```bash
deactivate
```

### 4. Install Python dependencies

With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify Python dependencies:

```bash
python3 -c "import ffmpeg, yaml; print('All Python dependencies OK')"
```

## Configuration

Configure your RTSP stream and recording settings via YAML:

```bash
cp config/config.yaml.example config/config.yaml
```

Edit `config/config.yaml` with your camera's RTSP URL and preferred settings.

## Usage

### Running the application

With the virtual environment activated:

```bash
cd /home/ruben/Projects/local_dvr
source .venv/bin/activate
python -m src.main
```

On first run, the application will attempt to connect to the configured RTSP stream. If successful, you'll see a connection confirmation. Use `Ctrl+C` to exit gracefully.

### Web-based live preview

When `display.enabled` is set to `true` (default), a web server will start serving a live MJPEG preview. After starting the application, open your browser and navigate to:

```
http://localhost:8080
```

If accessing from another device on the same network, replace `localhost` with the host machine's IP address.

The web preview logs frame activity every 5 seconds in the console.

### Configuration options

Key settings you can adjust:

- **RTSP URL**: Camera stream endpoint (required)
- **display.enabled**: Set to `false` to disable the web preview server
- **display.window_name**: Legacy setting (kept for compatibility, not used in web preview)
- **recording.enabled**: Enable/disable automatic recording
- **recording.output_dir**: Directory where recordings are saved (defaults to `./recordings`)
- **recording.codec**: Use `copy` to avoid re-encoding (faster, preserves quality) when possible
- **recording.segment_duration**: Split recordings into segments (in seconds). Default: 3600 (1 hour). If the process exits before reaching the segment duration, the current file will be properly closed.
- **rtsp.reconnect_interval**: Time between reconnection attempts on failure

## Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `No such file or directory: 'ffprobe'` | FFmpeg not installed or not in PATH | Run `sudo apt install ffmpeg` and verify with `ffprobe -version` |
| `No such file or directory: 'ffmpeg'` | FFmpeg not installed | Install FFmpeg as above |
| `The virtual environment was not created successfully because ensurepip is not available` | Missing `python3-venv` package | Run `sudo apt install python3-venv` |
| Cannot access web preview | Firewall or wrong URL | Ensure port 8080 is accessible; try `http://127.0.0.1:8080` from the same machine |
| Connection fails with auth error | Invalid credentials/URL | Double-check your RTSP URL format and credentials in `config.yaml` |
| Stream times out | Network/firewall issue | Verify camera is accessible on the network, try `ffprobe rtsp://...` manually to test |
| Permission errors writing recordings | Directory permissions | Ensure `recordings/` is writable, or change `output_dir` to a writable location |

## Features

- Web-based live MJPEG preview (toggleable via config)
- Recording to local storage (MP4 format)
- Hourly segmenting (1 hour per file) with proper cleanup on exit
- Graceful shutdown with Ctrl+C
- Configurable via YAML
