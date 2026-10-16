#!/usr/bin/env python3
import sys
import os
import logging
import signal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config
from stream import RTSPStream

def setup_logging(level='INFO'):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def signal_handler(signum, frame):
    logging.info("Shutdown requested...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
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

if __name__ == '__main__':
    main()
