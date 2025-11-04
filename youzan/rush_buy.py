import json
import logging
import time

from InquirerPy import inquirer

import config
import time_utils
from api import YouzanApi

api = YouzanApi()

### 加载配置文件
config_path = inquirer.filepath(
    message='请输入你的配置文件路径:',
    default='config.json'
).execute()
config.load_config(config_path)

### 加载抢购配置
rush_buy_config_path = inquirer.filepath(
    message='请输入抢购配置文件路径:',
    default='rush_buy_config.json'
).execute()

with open(rush_buy_config_path, 'r', encoding='utf-8') as f:
    rush_buy_config = json.load(f)

kdt_id = rush_buy_config['kdt_id']
goods_id = rush_buy_config['goods_id']
goods_title = rush_buy_config['goods_title']
sku_id = rush_buy_config['sku_id']
sku_price = rush_buy_config['sku_price']
property_ids = rush_buy_config['property_ids']
num = rush_buy_config['num']
delivery = rush_buy_config['delivery']
goods_start_sold_time_str = rush_buy_config['goods_start_sold_time_str']

### 等待商品开售
goods_start_sold_time = time_utils.time_str_to_timestamp(goods_start_sold_time_str, '%Y-%m-%d %H:%M:%S')
while True:
    countdown = goods_start_sold_time - int(time.time())
    logging.info(f'商品名称:{goods_title},商品价格:{sku_price},距离开售还有{countdown}秒')
    if 60 <= countdown:
        time.sleep(10)
    elif 1 <= countdown < 60:
        time.sleep(1)
    elif 0.1 <= countdown < 1:
        time.sleep(0.1)
    else:
        break

### 开始抢购商品
while True:
    try:
        order_buy_response = api.order_buy(kdt_id=kdt_id, goods_id=goods_id, sku_id=sku_id, property_ids=property_ids, num=num, delivery=delivery)
        logging.info(f'尝试抢购商品,返回结果:{order_buy_response.text}')
        if order_buy_response.json()['code'] == 0:
            logging.info('抢购商品成功,请在5分钟内打开小程序付款')
            break
    except Exception as e:
        logging.error(f'抢购商品失败,错误原因:{e.args}')
    finally:
        time.sleep(0.5)
