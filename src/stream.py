import ffmpeg
import logging

class RTSPStream:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.logger = logging.getLogger(__name__)

    def get_stream_info(self):
        try:
            probe = ffmpeg.probe(self.rtsp_url)
            return probe
        except Exception as e:
            self.logger.error(f"Failed to probe stream: {e}")
            raise

    def create_input(self):
        try:
            return ffmpeg.input(self.rtsp_url, rtsp_transport='tcp')
        except Exception as e:
            self.logger.error(f"Failed to create input: {e}")
            raise
