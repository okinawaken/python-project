import json

import encryption_utils

my_config = {
    "headers": {
    }
}


def load_config(config_path):
    global my_config
    with open(config_path, 'r', encoding='utf-8') as f:
        my_config = json.load(f)


def get_headers():
    time = encryption_utils.get_time()
    noice = encryption_utils.get_noice()
    signature = encryption_utils.get_signature(time=time, noice=noice)
    return {
        **my_config['headers'],
        'time': time,
        'noice': noice,
        'signature': signature
    }
