import json


def debug():
    return False


def get_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def get_headers():
    config = get_config()
    return config['headers']


def get_access_params():
    config = get_config()
    return config['access_params']


def get_goods_alias():
    config = get_config()
    # 【城市系列】光遇明信片 - 美好食光 I  ->  2xkoxethgm4e9g4
    # 【城市系列】光遇马口铁徽章 - 兰舟轻扬  -> 35x9meeyrdyldof
    # Sky x Le Petit Prince 毛绒别针钥匙扣挂饰 - 狐狸  ->  2opomy2cx91xdj6
    return config['goods_alias']


def get_purchase_num():
    config = get_config()
    return config['purchase_num']


def get_delivery():
    config = get_config()
    return config['delivery']
