import cv2
import logging

class Viewer:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.window_name = config['display'].get('window_name', 'RTSP Live View')
        self.running = False

    def display(self, frame):
        if not self.config['display'].get('enabled', True):
            return

        cv2.imshow(self.window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.running = False
            return False
        if key == ord('r'):
            return 'toggle_record'
        return True
