import sys
from wumai import config
from wumai.server.api import create_api
from wumai.server.worker import create_worker

__all__ = [
    'create_api',
    'create_worker',
    'ensure_app_root'
]


def ensure_config_setup():
    assert bool(config.CONF), 'config should setup first!'

    app_root = getattr(config.CONF, 'app_root')
    assert bool(app_root), 'app root is not set!'

    log_dir = getattr(config.CONF, 'log_dir')
    assert bool(log_dir), 'log dir is not set!'

    if app_root not in sys.path:
        sys.path.append(app_root)
