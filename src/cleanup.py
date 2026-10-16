import glob
import logging
import os
import re
import threading
import time

DEFAULT_RETENTION_DAYS = 30
DEFAULT_INTERVAL_HOURS = 24


def _pattern_to_glob(filename_pattern):
    # Convert a strftime filename pattern into a glob so cleanup only touches
    # files this application writes.
    #   recording_%Y%m%d_%H%M%S.mp4 -> recording_*.mp4
    return re.sub(r'%[a-zA-Z%]', '*', filename_pattern)


def delete_old_recordings(config, logger=None):
    logger = logger or logging.getLogger(__name__)

    retention = config.get('retention', {})
    if not retention.get('enabled', True):
        logger.debug("Retention disabled; skipping cleanup")
        return 0

    days = retention.get('days', DEFAULT_RETENTION_DAYS)
    if not days or days <= 0:
        logger.debug("Retention days not set; keeping all recordings")
        return 0

    recording = config.get('recording', {})
    output_dir = recording.get('output_dir', './recordings')
    if not os.path.isdir(output_dir):
        logger.debug(f"Recording directory does not exist: {output_dir}")
        return 0

    pattern = recording.get('filename_pattern')
    search = os.path.join(output_dir, _pattern_to_glob(pattern) if pattern else '*')

    cutoff = time.time() - days * 86400
    removed = 0
    for path in glob.glob(search):
        if not os.path.isfile(path):
            continue
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
                removed += 1
                logger.info(f"Deleted old recording: {path}")
        except OSError as e:
            logger.error(f"Failed to delete {path}: {e}")

    logger.info(f"Retention cleanup: removed {removed} file(s) older than {days} day(s)")
    return removed


class RetentionScheduler(threading.Thread):
    def __init__(self, config):
        super().__init__(name='retention-cleanup', daemon=True)
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stop_event = threading.Event()

    def run(self):
        retention = self.config.get('retention', {})
        if not retention.get('enabled', True):
            return

        interval = max(1, retention.get('interval_hours', DEFAULT_INTERVAL_HOURS)) * 3600

        self.logger.info(
            f"Retention cleanup active: removing recordings older than "
            f"{retention.get('days', DEFAULT_RETENTION_DAYS)} day(s) every "
            f"{interval // 3600}h"
        )
        delete_old_recordings(self.config, self.logger)
        while not self.stop_event.wait(interval):
            delete_old_recordings(self.config, self.logger)

    def stop(self):
        self.stop_event.set()


if __name__ == '__main__':
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import load_config

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    delete_old_recordings(load_config())
