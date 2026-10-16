import os
import datetime
import ffmpeg
import logging
import signal
import threading

class Recorder:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.process = None
        self.output_path = None
        self._stop_event = threading.Event()

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
        segment_duration = self.config['recording'].get('segment_duration', 3600)

        try:
            stream_kwargs = {
                'c': codec,
                'f': 'mp4',
                'movflags': '+faststart'
            }
            if segment_duration:
                stream_kwargs['segment_time'] = segment_duration
                stream_kwargs['reset_timestamps'] = 1

            stream = input_stream.output(self.output_path, **stream_kwargs)
            self.process = stream.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
            self.logger.info(f"Recording started: {self.output_path} (segment: {segment_duration}s)")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            raise

    def stop(self):
        if self.process is None:
            return

        try:
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

    def close(self):
        self.stop()

    def __del__(self):
        self.close()
