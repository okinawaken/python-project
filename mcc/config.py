import json

my_config = {
    "headers": {
    }
}


def load_config(config_path):
    global my_config
    with open(config_path, 'r', encoding='utf-8') as f:
        my_config = json.load(f)


def get_headers():
    return my_config['headers']
