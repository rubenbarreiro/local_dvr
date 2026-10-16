import cv2
import logging
import time

class Viewer:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.window_name = config['display'].get('window_name', 'RTSP Live View')
        self.running = False
        self.frame_count = 0
        self.last_log = time.time()

    def display(self, frame):
        if not self.config['display'].get('enabled', True):
            return True

        try:
            cv2.imshow(self.window_name, frame)
            self.frame_count += 1
            now = time.time()
            if now - self.last_log > 5:  # Log every 5 seconds
                fps_est = self.frame_count / (now - self.last_log) if (now - self.last_log) > 0 else 0
                self.logger.info(f"Live preview active - {self.frame_count} frames in last 5s (~{fps_est:.1f} fps)")
                self.frame_count = 0
                self.last_log = now
        except Exception as e:
            self.logger.error(f"Display error: {e}")
            return False

        try:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
                return False
            if key == ord('r'):
                return 'toggle_record'
            return True
        except Exception as e:
            self.logger.error(f"Key input error: {e}")
            return True
