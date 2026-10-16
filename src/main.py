#!/usr/bin/env python3
import sys
import os
import logging
import signal
import time
import numpy as np

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
    if viewer:
        try:
            import cv2
            cv2.destroyAllWindows()
        except Exception as e:
            logger.error(f"Error closing viewer: {e}")
    sys.exit(0)

def main():
    global recorder, stream, viewer
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
            input_stream = stream.create_input()
            recorder = Recorder(config)
            recorder.start(input_stream)
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            sys.exit(1)

    # Initialize viewer if display is enabled
    if config['display'].get('enabled', True):
        try:
            import cv2
            viewer = Viewer(config)
            logger.info(f"Live preview started (window: {viewer.window_name}). Press 'q' to quit, 'r' to toggle recording")
            try:
                probe = ffmpeg.probe(rtsp_url)
                video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
                width = int(video_stream['width']) if video_stream and 'width' in video_stream else 640
                height = int(video_stream['height']) if video_stream and 'height' in video_stream else 480
                process = (
                    ffmpeg
                    .input(rtsp_url, rtsp_transport='tcp')
                    .output('pipe:', format='rawvideo', pix_fmt='bgr24')
                    .run_async(pipe_stdout=True, pipe_stderr=True)
                )
                logger.info(f"Live preview active (resolution: {width}x{height}) - logs every 5s")
                while True:
                    in_bytes = process.stdout.read(width * height * 3)
                    if not in_bytes:
                        logger.warning("Preview stream ended")
                        break
                    frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
                    if not viewer.display(frame):
                        break
            except Exception as e:
                logger.error(f"Live preview error: {e}")
                logger.info("Continuing without live preview")
        except ImportError:
            logger.error("OpenCV not available. Disabling live preview.")
        except Exception as e:
            logger.error(f"Failed to start live preview: {e}")
    else:
        logger.info("Live preview disabled in configuration")
        try:
            signal.pause()
        except KeyboardInterrupt:
            pass

    try:
        if config['display'].get('enabled', True) and 'process' in locals() and process.poll() is None:
            pass  # already in loop
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        if recorder:
            recorder.stop()
        if viewer:
            try:
                import cv2
                cv2.destroyAllWindows()
            except Exception:
                pass
        logger.info("Application terminated")

if __name__ == '__main__':
    main()
