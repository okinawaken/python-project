import logging
import time

import requests

import common.utils.time_utils as time_utils
import config

### 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

### 第一步，查询店铺内在售商品
homepage_detail_response = requests.get(
    url='https://h5.youzan.com/wscdeco/homepage-detail.json',
    headers=config.get_headers(),
    params={
        'kdt_id': '164887806'
    }
)
logging.info(f'第一步，查询店铺内在售商品，返回结果：{homepage_detail_response.text}')

### 第二步，选择日期
tag_list_top = None
for component in homepage_detail_response.json()['data']['components']:
    if component['type'] == 'tag_list_top':
        tag_list_top = component
        break
print("第二步，请选择你想要购买的日期：")
for idx, tab in enumerate(tag_list_top['tabs'], 1):
    print(f"{idx}. {tab['tag_name']} {tab['alias']}")
choice = int(input("请输入对应的数字选择日期: ")) - 1
selected_tab = tag_list_top['tabs'][choice]
logging.info(f'第二步，选择购买的日期，{selected_tab}')

### 第三步，查询该日期下的商品
goods_by_tag_alias_response = requests.get(
    url='https://shop165079974.youzan.com/wscshop/goods-api/goodsByTagAlias.json',
    params={
        'kdt_id': '164887806',
        'alias': selected_tab['alias']
    }
)
logging.info(f'第三步，查询该日期下的商品，返回结果：{goods_by_tag_alias_response.text}')

### 第四步，显示商品并让用户选择
print("第四步，请选择要购买的商品：")
for idx, goods in enumerate(goods_by_tag_alias_response.json()['data']['list'], 1):
    print(f'{idx}. {goods['title']} 价格: ¥{goods['price']}')
choice = int(input('请输入对应的数字选择商品: ')) - 1
selected_goods = goods_by_tag_alias_response.json()['data']['list'][choice]
logging.info(f'第四步，选择的商品，{selected_goods}')

### 第五步，查询商品详细信息
goods_detail_response = requests.get(
    url='https://h5.youzan.com/wscgoods/tee-app/detail-v2.json',
    params={
        'alias': selected_goods['alias']
    }
)
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

### 第六步，等待商品开售
while not config.debug():
    countdown = goods_start_sold_time - int(time.time())
    logging.info(f'第六步，等待商品开售，还有{countdown}秒')

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
logging.info('第六步，等待商品开售结束，开始抢购商品')

### 第七步，抢购商品
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
                        'num': 1
                    }
                ],
                "propertyIds": [13009239],
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
