import os
import yaml

DEFAULT_CONFIG = {
    'rtsp': {
        'url': '',
        'reconnect_interval': 5,
    },
    'recording': {
        'enabled': True,
        'output_dir': './recordings',
        'filename_pattern': 'recording_%Y%m%d_%H%M%S.mp4',
        'segment_duration': 3600,  # 1 hour
        'codec': 'copy',
        'audio_codec': 'aac',
        'audio_bitrate': '64k',
        'fragmented': True,
        'max_muxing_queue': 128,
    },
    'display': {
        'enabled': False,
        'host': '0.0.0.0',
        'port': 8080,
    },
    'general': {
        'log_level': 'INFO',
    }
}

def load_config(config_path='config/config.yaml'):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        return merge_config(DEFAULT_CONFIG, config)
    return DEFAULT_CONFIG

def merge_config(default, user):
    result = default.copy()
    for key, value in user.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    return result
