import logging
import time
from datetime import datetime

from InquirerPy import inquirer
from InquirerPy.base import Choice

import config
from api import KlookApi

api = KlookApi()

# 加载配置文件
config_path = inquirer.filepath(
    message='请输入你的配置文件路径:',
    default='config.json'
).execute()
config.load_config(config_path)

# 输入program_uuid
program_uuid = inquirer.select(
    message='请输入 program_uuid:',
    choices=[
        Choice(name='酒店产品_5折优惠券', value='7caa8e0'),
        Choice(name='指定美食产品5折券', value='769027a'),
        Choice(name='阿倍野展望台门票 HARUKAS 300', value='9a0a5f1')
    ]
).execute()

# 输入抢购开始时间
rush_time_str = inquirer.text(
    message='请输入抢购开始时间（格式：HH:MM:SS）：',
    default='12:00:00'
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
    elif countdown >= 2:
        time.sleep(1)
    else:
        time.sleep(0.1)

# 开始抢购，失败后每隔0.3秒重试
while True:
    try:
        logging.info(f'尝试兑换优惠券...')
        response = api.manual_redeem(program_uuid=program_uuid)
        logging.info(f'响应内容: {response.text}')

        # 使用success字段判断是否成功
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logging.info(f'兑换成功! 响应: {response.text}')
                break
    except Exception as e:
        logging.error(f'兑换异常: {e}, 0.3秒后重试...')
    time.sleep(0.3)
