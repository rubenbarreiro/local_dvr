# Architectural Specification Document (ASD)
## Project: local_dvr

## 1. Overview
This project provides a solution to connect to a local RTSP stream from a WiFi camera, enabling recording (and optionally a web-based live preview). It is designed to run on low-power, low-memory hardware such as a Raspberry Pi Zero W (512 MB RAM, single-core ARMv6).

## 2. Goals and Objectives
- Connect to a local RTSP stream from a WiFi camera
- Provide recording functionality to local storage
- Provide an optional web-based live view
- Maintain a simple, maintainable, low-memory architecture

## 3. System Architecture

### 3.1 High-Level Components
- RTSP Source (WiFi Camera): Provides video stream via RTSP
- Stream Client: Connects to and probes the RTSP stream
- Recording Module: Remuxes the stream to segmented MP4 files on disk
- Preview Module (optional): Serves a web-based MJPEG live view
- Configuration Manager: Manages settings (RTSP URL, segment duration, storage paths, preview settings)

### 3.2 Data Flow
1. Application loads configuration
2. Stream Client probes the RTSP endpoint
3. Recording Module starts an FFmpeg process that remuxes packets directly to disk (no decoding, no Python buffering)
4. Recordings are split into segments; on shutdown the active segment is finalized
5. If enabled, the Preview Module decodes a low-cost MJPEG stream and serves it over HTTP

## 4. Technology Stack
- **Language**: Python
- **Stream handling**: FFmpeg via `ffmpeg-python` (`ffmpeg`/`ffprobe` binaries required)
- **Recording**: FFmpeg `-c copy` remux (video never decoded); audio transcoded to AAC
- **Live preview (optional)**: FFmpeg decoding to MJPEG, served by a Python `http.server`
- **Configuration**: YAML

## 5. Configuration
Configuration parameters include:
- RTSP URL (rtsp://user:pass@host:port/path)
- Recording settings (video codec, audio codec/bitrate, container, segment duration, fragmentation, muxing queue)
- Storage location and naming conventions
- Preview settings (enabled, host, port)

## 6. Functional Requirements
- FR-001: Connect to RTSP stream using provided URL
- FR-002: Record video stream to local storage as segmented MP4 files
- FR-003: Finalize the current segment on graceful shutdown
- FR-004: Provide an optional web-based live preview
- FR-005: Configure parameters via configuration file
- FR-006: Keep memory usage bounded regardless of recording duration

## 7. Non-Functional Requirements
- Low memory footprint (target: Raspberry Pi Zero W, 512 MB RAM)
- Video is remuxed, never decoded, during recording
- Efficient disk usage for recordings
- Graceful error handling and cleanup
- Crash/power-loss resilience for in-progress files (fragmented MP4)

## 8. Directory Structure
local_dvr/
├── docs/
│   └── ASD.md
├── config/
│   ├── config.yaml.example
│   └── config.yaml          # local, gitignored
├── src/
│   ├── stream.py            # RTSP probing
│   ├── recorder.py          # Segmented recording via FFmpeg
│   ├── viewer.py            # Web MJPEG preview server
│   ├── config.py            # Configuration management
│   └── main.py              # Application entry point
├── recordings/              # Default output directory
├── requirements.txt
├── README.md
└── .gitignore

## 9. Implementation Notes
- Use FFmpeg for robust RTSP handling (timeouts, reconnection, codec issues)
- Video is remuxed with `-c copy`; only audio is transcoded (AAC) because camera PCM is invalid in MP4
- Bound the muxer with `-max_muxing_queue_size`; use `-threads 1` on single-core targets
- Segment via FFmpeg's `segment` muxer with `-strftime`, `-reset_timestamps`
- Graceful shutdown via `q` on FFmpeg stdin (SIGINT/SIGTERM handled at app level)
- Timestamp recordings (e.g., recording_YYYYMMDD_HHMMSS.mp4)

## 10. Future Considerations
- Motion detection
- Multiple camera support
- Web-based management UI
- Storage management (auto-rotation/deletion/retention policy)
