# local_dvr

A simple DVR for local RTSP streams from WiFi cameras. Provides live viewing and recording functionality.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your RTSP stream in `config/config.yaml` (copy from example).

3. Run the application:
```bash
python -m src.main
```

## Configuration

Edit `config/config.yaml` with your camera's RTSP URL and preferred settings.

## Features
- Live view of RTSP stream
- Recording to local storage
- Configurable settings

## Environment Variables (Recommended)

For security, use a `.env` file instead of committing credentials:

```bash
cp .env.example .env
# Edit .env with your RTSP URL
```

The `.env` file is gitignored and will override config.yaml values.
