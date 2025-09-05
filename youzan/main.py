import logging
import time

from InquirerPy import inquirer
from InquirerPy.base import Choice

import config
from utils import time_utils
from youzan.api import YouzanApi

api = YouzanApi()

### 搜索商品
kdt_id = inquirer.select(
    message='请选择你想要搜索的店铺',
    choices=[
        Choice(value=140713009, name='店铺id：140713009 店铺名称：那家小铺'),
        Choice(value=164887806, name='店铺id：164887806，店铺名称：TinyRoll'),
        Choice(value=90605957, name='店铺id：90605957，店铺名称：Toris')
    ]
).execute()
keyword = inquirer.text(
    message='请输入你想要搜索的商品：'
).execute()
goods_search_response = api.goods_search(kdt_id=kdt_id, keyword=keyword)
goods_search_detail = inquirer.select(
    message='请选择你想购买的商品：',
    choices=[Choice(value=goods, name=f'商品id：{goods['id']} 商品标题：{goods['title']}') for goods in goods_search_response.json()['data']]
).execute()
sku_search_detail = inquirer.select(
    message='请选择你想购买的商品规格：',
    choices=[Choice(value=sku, name=f'商品规格id：{sku['sku_id']} 商品价格：{sku['price']}') for sku in goods_search_detail['sku_price_map'].values()]
).execute()

### 查询商品详情信息
goods_detail_v2_response = api.goods_detail_v2(alias=goods_search_detail['alias'])

### 可选，选择商品属性
property_ids = []
if 'itemSalePropList' in goods_detail_v2_response.json()['data']['goodsData']['goods']:
    for item_sale_properties in goods_detail_v2_response.json()['data']['goodsData']['goods']['itemSalePropList']:
        property_id = inquirer.select(
            message=f'请选择你想购买的商品属性，{item_sale_properties['k']}：',
            choices=[Choice(value=properties['id'], name=f'商品属性id：{properties['id']} 商品属性名称：{properties['name']}') for properties in item_sale_properties['v']]
        ).execute()
        property_ids.append(property_id)

### 选择商品数量
num = inquirer.number(
    message='请输入你想购买的商品数量：',
    default=1
).execute()

### 选择配送方式
delivery = {}
express_type_choice = inquirer.select(
    message='请选择你的配送方式：',
    choices=[
        choice for choice in [
            Choice(value={'expressType': 'express', 'expressTypeChoice': 0}, name='快递配送') if goods_detail_v2_response.json()['data']['goodsData']['delivery']['supportExpress'] else None,
            Choice(value={'expressType': 'self-fetch', 'expressTypeChoice': 1}, name='到店自提') if goods_detail_v2_response.json()['data']['goodsData']['delivery']['supportSelfFetch'] else None
        ] if choice is not None
    ]
).execute()
if express_type_choice['expressTypeChoice'] == 0:
    get_address_list_response = api.get_address_list()
    address_detail = inquirer.select(
        message='请选择你的收货地址：',
        choices=[Choice(value=address, name=f'{address['province']}{address['city']}{address['county']}{address['addressDetail']}') for address in get_address_list_response.json()['data']]
    ).execute()
    delivery = {
        **express_type_choice,
        'address': address_detail
    }
elif express_type_choice['expressTypeChoice'] == 1:
    self_fetch_address_list_response = api.get_self_fetch_address_list(kdt_id=kdt_id, goods_id=goods_search_detail['id'], sku_id=sku_search_detail['sku_id'], num=num)
    self_fetch_address_detail = inquirer.select(
        message='请选择你的自提地址：',
        choices=[Choice(value=self_fetch_address, name=f'{self_fetch_address['province']}{self_fetch_address['city']}{self_fetch_address['county']}{self_fetch_address['addressDetail']}') for
                 self_fetch_address in self_fetch_address_list_response.json()['data']['list']]
    ).execute()

    self_fetch_start_time = inquirer.text(
        message='请输入你的自提开始时间（格式示例：2025-09-05 13:00:00）：',
        default='2025-09-05 13:00:00'
    ).execute()
    self_fetch_end_time = inquirer.text(
        message='请输入你的自提结束时间（格式示例：2025-09-05 15:00:00）：',
        default='2025-09-05 15:00:00'
    ).execute()
    appointment_person = inquirer.text(
        message='请输入提货人姓名：'
    ).execute()
    appointment_tel = inquirer.text(
        message='请输入提货人手机号：'
    ).execute()

    appointment_date = time_utils.time_str_format(self_fetch_start_time, '%Y-%m-%d %H:%M:%S', '%m月%d日')
    appointment_start_time = time_utils.time_str_format(self_fetch_start_time, '%Y-%m-%d %H:%M:%S', '%H:%M')
    appointment_end_time = time_utils.time_str_format(self_fetch_end_time, '%Y-%m-%d %H:%M:%S', '%H:%M')

    self_fetch_detail = {
        **self_fetch_address_detail,
        'lat': str(self_fetch_address_detail['lat']),
        'lng': str(self_fetch_address_detail['lng']),
        'selfFetchStartTime': self_fetch_start_time,
        'selfFetchEndTime': self_fetch_end_time,
        'appointmentTime': f'{appointment_date} {appointment_start_time}-{appointment_end_time}',
        'appointmentPerson': appointment_person,
        'appointmentTel': appointment_tel
    }
    delivery = {
        **express_type_choice,
        'selfFetch': self_fetch_detail
    }
else:
    exit(0)

### 最后确认开售时间
goods_start_sold_time_str = inquirer.text(
    message='请确认商品开售时间：',
    default=time_utils.timestamp_to_time_str(goods_detail_v2_response.json()['data']['goodsData']['goods']['startSoldTime'] / 1000, '%Y-%m-%d %H:%M:%S')
).execute()

### 等待商品开售
goods_start_sold_time = time_utils.time_str_to_timestamp(goods_start_sold_time_str, '%Y-%m-%d %H:%M:%S')
while not config.debug():
    countdown = goods_start_sold_time - int(time.time())
    logging.info(f'商品名称：{goods_search_detail['title']}，商品价格：{sku_search_detail['price']}，距离开售还有{countdown}秒')
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
        order_buy_response = api.order_buy(kdt_id=kdt_id, goods_id=goods_search_detail['id'], sku_id=sku_search_detail['sku_id'], property_ids=property_ids, num=num, delivery=delivery)
        logging.info(f'尝试抢购商品，返回结果：{order_buy_response.text}')
        if order_buy_response.json()['code'] == 0:
            logging.info('抢购商品成功，请在5分钟内打开小程序付款')
            break
    except Exception as e:
        logging.error(f'抢购商品失败，错误原因：{e.args}')
    finally:
        time.sleep(0.5)
