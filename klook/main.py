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
    message='请选择 program_uuid:',
    choices=[
        Choice(name='酒店产品_5折优惠券', value='8a6d71f'),
        Choice(name='香港迪士尼立减30元券', value='be10a4c')
    ]
).execute()

# 输入抢购开始时间
rush_time_str = inquirer.text(
    message='请输入抢购开始时间（格式：HH:MM:SS.fff，例如 12:00:00.000）：',
    default='12:00:00.000'
).execute()

# 输入网络延迟补偿（毫秒）
network_compensation = float(inquirer.number(
    message='请输入网络延迟补偿（毫秒，建议100-200）：',
    default=200,
    min_allowed=0,
    max_allowed=2000
).execute())

# 解析抢购时间（精确到毫秒）
time_parts = datetime.strptime(rush_time_str, '%H:%M:%S.%f')
target_time = datetime.now().replace(
    hour=time_parts.hour,
    minute=time_parts.minute,
    second=time_parts.second,
    microsecond=time_parts.microsecond
)
# 保留高精度时间戳（浮点数，包含毫秒）
target_timestamp = target_time.timestamp()
# 提前发送请求以补偿网络延迟
target_timestamp -= network_compensation / 1000.0

# 等待倒计时（使用高精度时间）
while True:
    countdown = target_timestamp - time.time()
    if countdown <= 0:
        break
    elif countdown >= 60:
        logging.info(f'距离抢购开始还有 {countdown:.1f} 秒')
        time.sleep(10)
    elif countdown >= 2:
        logging.info(f'距离抢购开始还有 {countdown:.1f} 秒')
        time.sleep(1)
    elif countdown >= 0.5:
        logging.info(f'距离抢购开始还有 {countdown:.3f} 秒')
        time.sleep(0.1)
    else:
        # 最后0.5秒内使用高精度等待
        logging.info(f'距离抢购开始还有 {countdown:.3f} 秒')
        time.sleep(0.01)

# 开始抢购，失败后快速重试
while True:
    try:
        response = api.manual_redeem(program_uuid=program_uuid)
        logging.info(f'响应内容: {response.text}')

        # 使用success字段判断是否成功
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                break
    except Exception as e:
        logging.error(f'兑换异常: {e}')
    time.sleep(1)
