import os
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    'rtsp': {
        'url': '',
        'reconnect_interval': 5,
    },
    'recording': {
        'enabled': True,
        'output_dir': './recordings',
        'filename_pattern': 'recording_%Y%m%d_%H%M%S.mp4',
        'segment_duration': 300,
        'codec': 'copy',
    },
    'display': {
        'enabled': True,
        'window_name': 'RTSP Live View',
    },
    'general': {
        'log_level': 'INFO',
    }
}

def load_env_config():
    env_path = Path('.env')
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars

def load_config(config_path='config/config.yaml'):
    env = load_env_config()
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        config = merge_config(DEFAULT_CONFIG, config)
    else:
        config = DEFAULT_CONFIG.copy()
    
    # Override with env vars
    if env.get('RTSP_URL'):
        config['rtsp']['url'] = env['RTSP_URL']
    if env.get('RTSP_RECONNECT_INTERVAL'):
        try:
            config['rtsp']['reconnect_interval'] = int(env['RTSP_RECONNECT_INTERVAL'])
        except ValueError:
            pass
    
    return config

def merge_config(default, user):
    result = default.copy()
    for key, value in user.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    return result
