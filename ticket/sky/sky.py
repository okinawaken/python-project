import logging
import time

import requests

import common.utils.time_utils as time_utils
import config

### 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

### 第一步，查询商品详情信息
goods_detail_response = requests.get(
    url='https://h5.youzan.com/wscgoods/tee-app/detail-v2.json',
    params={
        'alias': config.get_goods_alias()
    }
)
if not goods_detail_response.json()['code'] == 0:
    logging.info(f'第一步，查询商品详情信息失败，请检查输入的商品别名是否正确，返回结果：{goods_detail_response.text}')
    exit(-1)
goods_title = goods_detail_response.json()['data']['goodsData']['goods']['title']
goods_start_sold_time = goods_detail_response.json()['data']['goodsData']['goods']['startSoldTime'] / 1000
kdt_id = goods_detail_response.json()['data']['goodsData']['goods']['kdtId']
goods_id = goods_detail_response.json()['data']['goodsData']['goods']['id']
sku_id = goods_detail_response.json()['data']['spuStock']['skuId']
sku_stock_num = goods_detail_response.json()['data']['spuStock']['stockNum']
logging.info(
    f'第一步，查询商品详情信息成功，商品名称：{goods_title}，'
    f'当前时间：{time_utils.timestamp_to_time_str(time.time(), '%Y-%m-%d %H:%M:%S')}，'
    f'商品起售时间：{time_utils.timestamp_to_time_str(goods_start_sold_time, '%Y-%m-%d %H:%M:%S)}')}，'
    f'店铺id：{kdt_id}，商品id：{goods_id}，sku-id：{sku_id}，sku库存数：{sku_stock_num}'
)

### 第二步，等待商品开售
while not config.debug():
    countdown = goods_start_sold_time - int(time.time())
    logging.info(f'第二步，等待商品开售，还有{countdown}秒')

    if 600 <= countdown:
        time.sleep(100)
    elif 60 <= countdown < 600:
        time.sleep(10)
    elif 1 <= countdown < 60:
        time.sleep(1)
    elif 0.1 <= countdown < 1:
        time.sleep(0.1)
    else:
        break
logging.info('第二步，等待商品开售结束，开始抢购商品')

### 第三步，抢购商品
while True:
    try:
        response = requests.post(
            'https://cashier.youzan.com/pay/wsctrade/order/buy/v2/bill-fast.json',
            headers=config.get_headers(),
            params=config.get_access_params(),
            json={
                'version': 2,
                'source': {},
                'config': {},
                'items': [
                    {
                        'kdtId': kdt_id,
                        'goodsId': goods_id,
                        'skuId': sku_id,
                        'num': config.get_purchase_num()
                    }
                ],
                'delivery': config.get_delivery()
            }
        )
        logging.info(f'第三步，抢购商品，返回结果：{response.text}')
        if response.json()['code'] == 0:
            logging.info('第三步，抢购商品成功，请在5分钟内打开小程序进行付款')
            break
    except Exception as e:
        logging.error(f'第三步，抢购商品失败，错误原因：{e.args}')
    finally:
        time.sleep(0.3)
