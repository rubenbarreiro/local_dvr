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

    def _generate_filename(self):
        pattern = self.config['recording']['filename_pattern']
        timestamp = datetime.datetime.now().strftime(pattern)
        output_dir = self.config['recording']['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, timestamp)

    def start(self, input_stream):
        if self.process is not None:
            self.logger.warning("Recording already in progress")
            return

        self.output_path = self._generate_filename()
        codec = self.config['recording'].get('codec', 'copy')
        segment_duration = self.config['recording'].get('segment_duration')

        try:
            stream = input_stream.output(
                self.output_path,
                c=codec,
                f='mp4',
                **({'segment_time': segment_duration, 'reset_timestamps': 1} if segment_duration else {})
            )
            self.process = stream.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
            self.logger.info(f"Recording started: {self.output_path}")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            raise

    def stop(self):
        if self.process is None:
            return

        try:
            self.process.stdin.write(b'q')
            self.process.communicate(timeout=5)
            self.process = None
            self.logger.info(f"Recording stopped: {self.output_path}")
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            if self.process:
                self.process.kill()
                self.process = None
