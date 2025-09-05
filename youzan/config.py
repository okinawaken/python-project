import json


def get_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def get_headers():
    config = get_config()
    return config['headers']


def get_access_params():
    config = get_config()
    return config['access_params']
