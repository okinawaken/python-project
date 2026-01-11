import re
import time
import logging
from datetime import datetime, timedelta

from InquirerPy import inquirer
from InquirerPy.base import Choice

import config
from api import MccApi

api = MccApi()

# 加载配置文件
config_path = inquirer.filepath(
    message='请输入你的配置文件路径:',
    default='config.json'
).execute()
config.load_config(config_path)

# 选择城市
city_id = inquirer.select(
    message='请选择你的城市：',
    choices=[
        Choice(value='52', name='北京'),
        Choice(value='321', name='上海'),
        Choice(value='76', name='广州'),
        Choice(value='77', name='深圳')
    ]
).execute()

# 选择场馆类型
mer_type = inquirer.select(
    message='请选择场馆类型：',
    choices=[
        Choice(value='swimbod', name='游泳健身'),
        Choice(value='yoga', name='瑜伽团课')
    ]
).execute()

# 查询场馆列表
get_mer_list_response = api.get_mer_list(mer_type=mer_type, city_id=city_id)

# 选择场馆
selected_mer = inquirer.select(
    message='请选择场馆：',
    choices=[Choice(value=item, name=item['name']) for item in get_mer_list_response.json()['data']['items'].values()]
).execute()

# 获取场馆详细信息以提取ids和token
get_mer_item_info_response = api.get_mer_item_info(
    mer_item_id=selected_mer['mer_item_id'],
    mer_type=mer_type
)

# 从HTML中提取ids
ids_match = re.search(r"<input type='hidden' id='ids' value=\"(\d+)\"", get_mer_item_info_response.text)
ids = ids_match.group(1)

# 从HTML中提取token
token_match = re.search(r"[&?]token=([^'&]+)", get_mer_item_info_response.text)
token = token_match.group(1)

# 选择日期
selected_date = inquirer.select(
    message='请选择预约日期：',
    choices=[Choice(value=(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'), name=(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')) for i in range(3)]
).execute()

# 查询该日期的可用时间段
time_response = api.get_valid_price_time(
    mer_item_id=selected_mer['mer_item_id'],
    date=selected_date,
    ids=ids
)

# 选择时间
selected_hour = inquirer.select(
    message='请选择预约时间：',
    choices=[Choice(value=hour.split(':')[0], name=hour) for hour in time_response.json()['data']['showHourStr'].split(',')]
).execute()

# 输入抢购开始时间
rush_time_str = inquirer.text(
    message='请输入抢购开始时间（格式：HH:MM:SS）：',
    default='10:00:00'
).execute()

# 解析抢购时间
time_parts = datetime.strptime(rush_time_str, '%H:%M:%S')
target_time = datetime.now().replace(hour=time_parts.hour, minute=time_parts.minute, second=time_parts.second, microsecond=0)
target_timestamp = int(target_time.timestamp())

# 等待倒计时
while True:
    countdown = target_timestamp - int(time.time())
    logging.info(f'距离抢购开始还有 {countdown} 秒')
    if countdown <= 0:
        break
    elif countdown >= 60:
        time.sleep(10)
    elif countdown >= 1:
        time.sleep(1)
    else:
        time.sleep(0.1)

# 开始抢购,失败后每隔1秒重试
while True:
    try:
        logging.info(f'尝试创建订单...')
        order_response = api.create_order(
            mer_item_id=selected_mer['mer_item_id'],
            book_day=selected_date,
            hour=selected_hour,
            mer_type=mer_type,
            token=token
        )
        logging.info(f'订单响应: {order_response.text}')
        # 使用正则表达式判断是否成功
        if order_response.status_code == 200:
            # 匹配成功文案
            if re.search(r'(预约成功|订单成功|下单成功|购买成功)', order_response.text):
                logging.info(f'抢购成功! 响应: {order_response.text}')
                break
            # 匹配失败文案
            elif re.search(r'(已约满|名额已满|已售罄|库存不足|预约失败|订单失败|请选择其他日期|未开始|已结束|尚未开始|活动结束)', order_response.text):
                logging.warning(f'抢购失败(已约满或库存不足或未开始/已结束),1秒后重试...')
            else:
                logging.warning(f'抢购状态未知,1秒后重试...')
        else:
            logging.warning(f'请求失败,状态码: {order_response.status_code},1秒后重试...')
    except Exception as e:
        logging.error(f'创建订单异常: {e}, 1秒后重试...')
    time.sleep(1)
