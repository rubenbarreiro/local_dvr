import os
import ffmpeg
import logging


class Recorder:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.process = None
        self.output_pattern = None

    def _build_output_pattern(self):
        output_dir = self.config['recording']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        pattern = self.config['recording']['filename_pattern']
        return os.path.join(output_dir, pattern)

    def start(self, rtsp_url):
        if self.process is not None:
            self.logger.warning("Recording already in progress")
            return

        rec = self.config['recording']
        self.output_pattern = self._build_output_pattern()
        codec = rec.get('codec', 'copy')
        audio_codec = rec.get('audio_codec', 'aac')
        audio_bitrate = rec.get('audio_bitrate', '64k')
        segment_duration = rec.get('segment_duration', 3600)
        fragmented = rec.get('fragmented', True)
        max_muxing_queue = rec.get('max_muxing_queue', 128)

        # Video is always remuxed (never decoded) so memory stays flat; only the
        # tiny audio stream is re-encoded (camera PCM is not valid in MP4).
        output_kwargs = {
            'vcodec': 'copy' if codec == 'copy' else codec,
            'acodec': audio_codec,
            'audio_bitrate': audio_bitrate,
            'f': 'segment',
            'segment_format': 'mp4',
            'reset_timestamps': 1,
            'strftime': 1,
            'loglevel': 'error',
            'max_muxing_queue_size': max_muxing_queue,
            'threads': 1,
        }
        if fragmented:
            output_kwargs['segment_format_options'] = (
                'movflags=+frag_keyframe+empty_moov+default_base_moof'
            )
        if segment_duration:
            output_kwargs['segment_time'] = segment_duration

        try:
            input_stream = ffmpeg.input(rtsp_url, rtsp_transport='tcp')
            stream = input_stream.output(self.output_pattern, **output_kwargs)
            self.process = stream.run_async(pipe_stdin=True)
            self.logger.info(
                f"Recording started: {self.output_pattern} "
                f"(segment: {segment_duration}s, codec: {codec})"
            )
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            raise

    def stop(self):
        if self.process is None:
            return

        try:
            # 'q' on stdin makes ffmpeg finalize the current segment gracefully
            self.process.stdin.write(b'q\n')
            self.process.stdin.flush()
            try:
                self.process.wait(timeout=10)
            except Exception:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except Exception:
                    self.process.kill()
            self.logger.info(f"Recording stopped: {self.output_pattern}")
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            if self.process:
                try:
                    self.process.kill()
                except Exception:
                    pass
        finally:
            self.process = None

    def close(self):
        self.stop()

    def __del__(self):
        self.close()
