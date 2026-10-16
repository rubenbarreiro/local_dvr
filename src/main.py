#!/usr/bin/env python3
import sys
import os
import logging
import signal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ffmpeg

from config import load_config
from stream import RTSPStream
from recorder import Recorder
from viewer import Viewer

recorder = None
stream = None
viewer = None
preview_process = None

def setup_logging(level='INFO'):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def signal_handler(signum, frame):
    logger = logging.getLogger(__name__)
    logger.info("Shutdown requested...")
    if recorder:
        try:
            recorder.stop()
        except Exception as e:
            logger.error(f"Error stopping recorder: {e}")
    if preview_process:
        try:
            preview_process.terminate()
        except Exception as e:
            logger.error(f"Error stopping preview: {e}")
    if viewer:
        try:
            viewer.stop()
        except Exception as e:
            logger.error(f"Error stopping viewer: {e}")
    sys.exit(0)

def main():
    global recorder, stream, viewer, preview_process
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = load_config()
    setup_logging(config['general']['log_level'])
    logger = logging.getLogger(__name__)
    
    rtsp_url = config['rtsp']['url']
    if not rtsp_url:
        logger.error("RTSP URL not configured. Please set it in config/config.yaml")
        sys.exit(1)
    
    logger.info(f"Connecting to RTSP stream: {rtsp_url}")
    stream = RTSPStream(rtsp_url)
    
    try:
        info = stream.get_stream_info()
        logger.info("Stream connected successfully")
        logger.info("Use Ctrl+C to exit")
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        sys.exit(1)

    if config['recording'].get('enabled', True):
        try:
            recorder = Recorder(config)
            recorder.start(rtsp_url)
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            sys.exit(1)

    if config['display'].get('enabled', True):
        try:
            viewer = Viewer(config)
            viewer.start_server()
            try:
                probe = ffmpeg.probe(rtsp_url)
                video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
                width = int(video_stream['width']) if video_stream and 'width' in video_stream else 640
                height = int(video_stream['height']) if video_stream and 'height' in video_stream else 480
                # loglevel=error keeps ffmpeg quiet; stderr is inherited (not a
                # pipe) so it can never fill up and block the process.
                preview_process = (
                    ffmpeg
                    .input(rtsp_url, rtsp_transport='tcp')
                    .output('pipe:', format='mjpeg', qscale=5, loglevel='error')
                    .run_async(pipe_stdout=True)
                )
                logger.info(f"Web preview active (resolution: {width}x{height}) - serving MJPEG stream")
                buffer = bytearray()
                max_buffer = 4 * 1024 * 1024
                while True:
                    chunk = preview_process.stdout.read(4096)
                    if not chunk:
                        logger.warning("Preview stream ended")
                        break
                    buffer.extend(chunk)
                    while True:
                        start = buffer.find(b'\xff\xd8')
                        end = buffer.find(b'\xff\xd9')
                        if start != -1 and end != -1 and end > start:
                            frame = bytes(buffer[start:end + 2])
                            del buffer[:end + 2]
                            viewer.update_frame(frame)
                        else:
                            break
                    if len(buffer) > max_buffer:
                        # Drop garbage/partial frame if no complete JPEG is found
                        start = buffer.rfind(b'\xff\xd8')
                        if start > 0:
                            del buffer[:start]
                        else:
                            buffer.clear()
            except Exception as e:
                logger.error(f"Web preview error: {e}")
                logger.info("Continuing without live preview")
        except Exception as e:
            logger.error(f"Failed to start web preview: {e}")
    else:
        try:
            signal.pause()
        except KeyboardInterrupt:
            pass

    try:
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        if recorder:
            recorder.stop()
        if preview_process:
            try:
                preview_process.terminate()
            except Exception:
                pass
        if viewer:
            try:
                viewer.stop()
            except Exception:
                pass
        logger.info("Application terminated")

if __name__ == '__main__':
    main()
