# local_dvr

A simple DVR for local RTSP streams from WiFi cameras. Provides live viewing and recording functionality.

## Prerequisites (Ubuntu/Debian-based systems)

Before installing, ensure you have the following system dependencies:

- **FFmpeg**: Required for RTSP stream handling, probing, and recording (`ffmpeg` and `ffprobe`)
- **OpenCV system libraries**: Required for live view display (`cv2.imshow`)
- **Python 3.8+**: Tested with Python 3.14
- **python3-venv**: Required for creating isolated Python virtual environments

## Installation

### 1. Update package lists

```bash
sudo apt update
```

### 2. Install system dependencies

Install FFmpeg, OpenCV system libraries, and Python venv support:

```bash
sudo apt install -y ffmpeg python3-venv libgl1 libglib2.0-0
```

Verify FFmpeg installation:

```bash
ffmpeg -version && ffprobe -version
```

> **Note:** If you're running on a headless server without a GUI/display server, you can skip live view by disabling it in your configuration (see Configuration section). The `libgl1` package is mainly needed for GUI display functionality.

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
python3 -c "import ffmpeg, cv2, yaml; print('All Python dependencies OK')"
```

## Configuration

You have two options for configuring your RTSP stream credentials. Using a `.env` file is **strongly recommended** to avoid committing sensitive credentials to version control.

### Option 1: Environment variables (.env) - Recommended

```bash
cp .env.example .env
```

Edit `.env` with your preferred editor and set your RTSP URL:

```bash
RTSP_URL=rtsp://username:password@192.168.1.100:554/stream
```

> The `.env` file is gitignored and will override values in `config.yaml`.

### Option 2: YAML configuration

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

### Configuration options

Key settings you can adjust:

- **RTSP URL**: Camera stream endpoint
- **display.enabled**: Set to `false` for headless operation (no GUI). If running without a display server, disable this to avoid `cv2.imshow` errors.
- **recording.enabled**: Enable/disable automatic recording
- **recording.output_dir**: Directory where recordings are saved (defaults to `./recordings`)
- **recording.codec**: Use `copy` to avoid re-encoding (faster, preserves quality) when possible
- **recording.segment_duration**: Split recordings into segments (in seconds)
- **rtsp.reconnect_interval**: Time between reconnection attempts on failure

## Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `No such file or directory: 'ffprobe'` | FFmpeg not installed or not in PATH | Run `sudo apt install ffmpeg` and verify with `ffprobe -version` |
| `No such file or directory: 'ffmpeg'` | FFmpeg not installed | Install FFmpeg as above |
| `The virtual environment was not created successfully because ensurepip is not available` | Missing `python3-venv` package | Run `sudo apt install python3-venv` |
| `cv2.imshow` fails / OpenGL errors | Missing OpenCV system libs or no display server | Install `libgl1 libglib2.0-0`, or set `display.enabled: false` for headless mode |
| Connection fails with auth error | Invalid credentials/URL | Double-check your RTSP URL format and credentials in `.env` or `config.yaml` |
| Stream times out | Network/firewall issue | Verify camera is accessible on the network, try `ffprobe rtsp://...` manually to test |
| Permission errors writing recordings | Directory permissions | Ensure `recordings/` is writable, or change `output_dir` to a writable location |

## Features

- Live view of RTSP stream
- Recording to local storage (MP4 format)
- Timestamped recordings with optional segmentation
- Environment variable support for secure credential management
- Graceful shutdown with Ctrl+C
- Configurable via YAML or environment variables
