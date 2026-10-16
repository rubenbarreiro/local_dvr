import logging
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class MJPEGHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.frame_broker = kwargs.pop('frame_broker', None)
        super().__init__(*args, **kwargs)

    def log_message(self, fmt, *args):
        return  # Suppress default HTTP logs

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html>
<head>
<title>RTSP Live Preview</title>
<style>
body { margin: 0; background: #000; text-align: center; }
img { max-width: 100vw; max-height: 100vh; }
</style>
</head>
<body>
<img src="/stream.mjpg" alt="Live stream" />
<script>
setInterval(() => {
  const img = document.querySelector('img');
  img.src = '/stream.mjpg?' + new Date().getTime();
}, 1000);
</script>
</body>
</html>'''
            self.wfile.write(html.encode())
            return
        elif self.path.startswith('/stream.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            last_frame = None
            while True:
                try:
                    frame = self.frame_broker.get_latest_frame() if self.frame_broker else None
                    if frame is not None and frame != last_frame:
                        last_frame = frame
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(frame)))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.1)
                except Exception:
                    break
            return
        else:
            self.send_error(404)
            return


class FrameBroker:
    def __init__(self):
        self.latest_frame = None
        self.lock = threading.Lock()

    def update_frame(self, frame_bytes):
        with self.lock:
            self.latest_frame = frame_bytes

    def get_latest_frame(self):
        with self.lock:
            return self.latest_frame


class Viewer:
    def __init__(self, config, host='0.0.0.0', port=8080):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.running = False
        self.frame_count = 0
        self.last_log = time.time()
        self.frame_broker = FrameBroker()
        self.server = None
        self.server_thread = None

    def start_server(self):
        if self.server:
            return

        def handler(*args, **kwargs):
            kwargs['frame_broker'] = self.frame_broker
            MJPEGHandler(*args, **kwargs)

        self.server = HTTPServer((self.host, self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        self.running = True
        self.logger.info(f"Web preview server started at http://{self.host}:{self.port}")
        self.logger.info(f"Access via: http://localhost:{self.port} or http://<your-ip>:{self.port}")

    def update_frame(self, frame_bytes):
        self.frame_broker.update_frame(frame_bytes)
        self.frame_count += 1
        now = time.time()
        if now - self.last_log > 5:
            fps_est = self.frame_count / (now - self.last_log) if (now - self.last_log) > 0 else 0
            self.logger.info(f"Web preview active - {self.frame_count} frames in last 5s (~{fps_est:.1f} fps)")
            self.frame_count = 0
            self.last_log = now

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception as e:
                self.logger.error(f"Error stopping server: {e}")
            self.server = None
