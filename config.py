import argparse
import json

from recognition import RecognitionOpt


class ConfigOpt:
    def __init__(self, config):
        self.bot = RecBotOpt(config['bot'])
        self.notify = NotifyOpt(config['notify'])
        self.rec = RecognitionOpt(config['rec'])
        self.camera = CameraOpt(config['camera'])


class NotifyOpt:
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']


class CameraOpt:
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']
        self.camera = config['camera']
        self.notify_api = config['notify_api']


def auto_load_config() -> ConfigOpt:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json', help='config file')
    args = parser.parse_args()
    return ConfigOpt(json.load(open(args.config)))


class RecBotOpt:
    def __init__(self, config):
        self.telegram_token = config['telegram_token']
        self.telegram_chat_id = config['telegram_chat_id']
        self.camera_api = config['camera_api']
        self.alert_color = config['alert_color']
