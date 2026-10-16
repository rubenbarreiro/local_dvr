# Architectural Specification Document (ASD)
## Project: local_dvr

## 1. Overview
This project provides a solution to connect to a local RTSP stream from a WiFi camera, enabling live viewing and recording capabilities.

## 2. Goals and Objectives
- Connect to a local RTSP stream from a WiFi camera
- Provide live view functionality
- Provide recording functionality to local storage
- Maintain a simple, maintainable architecture

## 3. System Architecture

### 3.1 High-Level Components
- RTSP Source (WiFi Camera): Provides video stream via RTSP
- Stream Client: Connects to and consumes the RTSP stream
- Video Processor: Handles decoding and processing of frames
- Display Module: Renders live video feed
- Recording Module: Saves video to disk in appropriate format
- Configuration Manager: Manages settings (RTSP URL, resolution, framerate, storage paths)

### 3.2 Data Flow
1. Application loads configuration
2. Stream Client establishes connection to RTSP endpoint
3. Frames are received and decoded
4. Frames are displayed in real-time (live view)
5. Frames are encoded and written to file (recording)
6. Application handles errors/reconnection as needed

## 4. Technology Stack
- **Language**: Python
- **Stream handling**: FFmpeg (via subprocess or ffmpeg-python/pyav)
- **Video processing**: FFmpeg for efficient recording, optional OpenCV if needed for preview
- **Configuration**: YAML/JSON/.env for settings
- **CLI/Interface**: CLI-based control (start/stop record, view status)

## 5. Configuration
Configuration parameters will include:
- RTSP URL (rtsp://user:pass@host:port/path)
- Stream resolution and framerate
- Recording settings (codec, container format, segment duration, max file size)
- Storage location and naming conventions
- Reconnection behavior and timeout settings

## 6. Functional Requirements
- FR-001: Connect to RTSP stream using provided URL
- FR-002: Display live video stream
- FR-003: Record video stream to local storage
- FR-004: Start/stop recording on demand
- FR-005: Handle connection failures with reconnection logic
- FR-006: Configure parameters via configuration file

## 7. Non-Functional Requirements
- Low latency for live view
- Efficient disk usage for recordings
- Graceful error handling and cleanup
- Cross-platform compatibility (Linux/Windows/macOS)

## 8. Directory Structure
local_dvr/
├── docs/
│   └── ASD.md
├── config/
│   └── config.yaml (or .env.example)
├── src/
│   ├── __init__.py
│   ├── stream.py      # RTSP stream handling
│   ├── recorder.py    # Recording logic
│   ├── viewer.py      # Live view display
│   ├── config.py      # Configuration management
│   └── main.py        # Application entry point
├── recordings/         # Default output directory
├── requirements.txt
├── README.md
└── .gitignore

## 9. Implementation Notes
- Use FFmpeg for robust RTSP handling (handles timeouts, reconnection, codec issues)
- Consider using `ffmpeg-python` for programmatic control, or direct subprocess
- Implement proper signal handling (SIGINT) for graceful shutdown
- Timestamp recordings (e.g., recording_YYYYMMDD_HHMMSS.mp4)

## 10. Future Considerations
- Motion detection
- Multiple camera support
- Web-based UI
- Storage management (auto-rotation/deletion)
