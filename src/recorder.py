import os
import datetime
import ffmpeg
import logging

class Recorder:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.process = None
        self.output_path = None
        self.input_stream = None

    def _generate_filename(self):
        pattern = self.config['recording']['filename_pattern']
        timestamp = datetime.datetime.now().strftime(pattern)
        output_dir = self.config['recording']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, timestamp)

    def start(self, rtsp_url):
        if self.process is not None:
            self.logger.warning("Recording already in progress")
            return

        self.output_path = self._generate_filename()
        codec = self.config['recording'].get('codec', 'copy')
        segment_duration = self.config['recording'].get('segment_duration', 3600)

        try:
            input_stream = ffmpeg.input(rtsp_url, rtsp_transport='tcp')
            output_kwargs = {
                'vcodec': codec if codec != 'copy' else 'copy',
                'an': None,
                'f': 'mp4',
            }
            if codec == 'copy' and segment_duration:
                output_kwargs['segment_time'] = segment_duration
                output_kwargs['reset_timestamps'] = 1
            elif segment_duration and codec != 'copy':
                output_kwargs['segment_time'] = segment_duration
                output_kwargs['reset_timestamps'] = 1

            stream = input_stream.output(self.output_path, **output_kwargs)
            self.process = stream.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
            self.logger.info(f"Recording started: {self.output_path} (segment: {segment_duration}s)")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            raise

    def stop(self):
        if self.process is None:
            return

        try:
            try:
                self.process.stdin.write(b'q\n')
                self.process.stdin.flush()
            except Exception:
                pass
            try:
                self.process.wait(timeout=15)
            except Exception:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                except Exception:
                    self.process.kill()
            self.process = None
            self.logger.info(f"Recording stopped: {self.output_path}")
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            if self.process:
                try:
                    self.process.kill()
                except Exception:
                    pass
                self.process = None
