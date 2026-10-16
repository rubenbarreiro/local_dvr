# local_dvr

A simple DVR for local RTSP streams from WiFi cameras. Record-only by default, with an optional web-based live preview. Designed to run comfortably on low-power hardware such as a Raspberry Pi Zero W.

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

On first run, the application will attempt to connect to the configured RTSP stream. If successful, it starts recording and logs a confirmation. Use `Ctrl+C` to exit gracefully; the in-progress segment is finalized on exit.

### Web-based live preview

Live preview is **disabled by default** (`display.enabled: false`). This is intentional: low-power targets cannot comfortably decode and serve video while recording.

To enable it, set `display.enabled: true`. A web server will then serve a live MJPEG preview at:

```
http://localhost:8080
```

If accessing from another device on the same network, replace `localhost` with the host machine's IP address. The preview logs frame activity every 5 seconds in the console.

> Note: when enabled, the preview opens a **second connection to the camera**. Many WiFi cameras allow only 1–2 concurrent connections, which can starve the recorder.

### Configuration options

Key settings you can adjust:

- **rtsp.url**: Camera stream endpoint (required)
- **rtsp.reconnect_interval**: Time between reconnection attempts on failure
- **recording.enabled**: Enable/disable automatic recording
- **recording.output_dir**: Directory where recordings are saved (defaults to `./recordings`)
- **recording.segment_duration**: Split recordings into segments (in seconds). Default: 3600 (1 hour). If the process exits before reaching the segment duration, the current file is properly closed.
- **recording.codec**: Video codec. Keep `copy` so video is remuxed, never decoded (low CPU/memory).
- **recording.audio_codec** / **recording.audio_bitrate**: Camera PCM audio is re-encoded to AAC (required for MP4).
- **recording.fragmented**: Write fragmented MP4 so a partially written segment survives a crash or power loss.
- **recording.max_muxing_queue**: Maximum packets buffered by the muxer (bounds memory on slow storage).
- **display.enabled**: Enable/disable the web preview server (default `false`)
- **display.host** / **display.port**: Bind address and port for the web preview

## Raspberry Pi Zero W notes

This project targets low-power, low-memory hardware (Raspberry Pi Zero W, 512 MB RAM, single-core ARMv6). Design choices:

- **Videos are streamed straight to disk.** `ffmpeg` runs with `-c copy` for video, so frames are never decoded and never buffered in memory. Peak memory of the recorder process is only a few MB.
- **No Python-side video buffering.** If you add features, do not read video frames into Python.
- **Only audio is re-encoded** (camera PCM -> AAC), which is cheap and required for MP4 compatibility.
- **Segments are crash-resilient** (fragmented MP4) so a partially written file remains playable after a power loss.
- **Live preview is off by default.** Software H.264 decode is not viable on ARMv6; enable only on more capable hardware.
- The `-max_muxing_queue_size` bound and `-threads 1` keep the recorder within budget on slow SD cards and a single CPU core.

### Installation on the Pi

Use the distribution's `ffmpeg` (armhf), **not** a static x86 build:

```bash
sudo apt update
sudo apt install -y ffmpeg python3-venv
ffmpeg -version
```

Then follow the virtual environment and configuration steps above.

### SD card considerations

- Recordings are written continuously and can fill the SD card quickly. Monitor free space with `df -h` and periodically move old files off the device.
- Prefer a high-endurance SD card; continuous writes wear out cheap cards.
- There is currently no automatic retention/rotation policy; manage files manually.

## Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `No such file or directory: 'ffprobe'` | FFmpeg not installed or not in PATH | Run `sudo apt install ffmpeg` and verify with `ffprobe -version` |
| `No such file or directory: 'ffmpeg'` | FFmpeg not installed | Install FFmpeg as above |
| `The virtual environment was not created successfully because ensurepip is not available` | Missing `python3-venv` package | Run `sudo apt install python3-venv` |
| Web preview stutters / Pi becomes unresponsive | Software decoding too heavy | Keep `display.enabled: false` on the Pi |
| Cannot access web preview | Firewall or wrong URL | Ensure port 8080 is accessible; try `http://127.0.0.1:8080` from the same machine |
| Connection fails with auth error | Invalid credentials/URL | Double-check your RTSP URL format and credentials in `config.yaml` |
| Stream times out | Network/firewall issue | Verify camera is accessible on the network, try `ffprobe rtsp://...` manually to test |
| Permission errors writing recordings | Directory permissions | Ensure `recordings/` is writable, or change `output_dir` to a writable location |
| Recording file is empty / unplayable | Audio codec incompatible with MP4 | Ensure `audio_codec: "aac"` (default); camera PCM cannot be stored in MP4 directly |
| Recordings fill the SD card | No retention policy | Manually rotate/delete old files; monitor free space |

## Features

- Recording to local storage (MP4, video remuxed with `-c copy`, audio transcoded to AAC)
- Segmented files (default 1 hour) with proper finalization on exit
- Fragmented MP4 segments (crash/power-loss resilient)
- Optional web-based live MJPEG preview (disabled by default; not recommended on low-power hardware)
- Graceful shutdown with Ctrl+C
- Configurable via YAML
- Low memory footprint suitable for Raspberry Pi Zero W
