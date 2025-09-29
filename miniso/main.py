import logging
import time

from InquirerPy import inquirer
from InquirerPy.base import Choice

import config
import time_utils
from api import MinisoApi

api = MinisoApi()

### 加载配置文件
config_path = inquirer.filepath(
    message='请输入你的配置文件路径：',
    default='config.json'
).execute()
config.load_config(config_path)

### 查询活动页面
activity_page_id = inquirer.select(
    message='请选择你想要访问的活动页面：',
    choices=[
        Choice(value=6665, name='id：6655 名称：第五人格快闪活动预约')
    ]
).execute()
activity_page_detail_response = api.get_activity_page_detail(activity_page_id=activity_page_id)
activity_page_json_response = api.get_activity_page_json(json_url=activity_page_detail_response.json()['data']['pageDetails']['jsonUrl'])
activity_code = activity_page_json_response.json()[0]['data']['actId']

### 查询活动详情
activity_detail_response = api.get_activity_detail(activity_code=activity_code)
activity_id = str(activity_detail_response.json()['data']['id'])

### 确认活动详情
activity_begin_time = inquirer.text(
    message='请确认活动开始时间：',
    default=activity_detail_response.json()['data']['activityBeginTime']
).execute()

session_begin_time = inquirer.text(
    message='请输入场次开始时间：',
    default='2025-09-28 12:00:00'
).execute()

### 等待活动开始
while True:
    countdown = time_utils.time_str_to_timestamp(activity_begin_time, '%Y/%m/%d %H:%M:%S') - int(time.time())
    logging.info(f'id：{activity_id}，名称：{activity_detail_response.json()['data']['activityName']}，距离活动开始还有{countdown}秒')
    if 60 <= countdown:
        time.sleep(10)
    elif 1 <= countdown < 60:
        time.sleep(1)
    elif 0.1 <= countdown < 1:
        time.sleep(0.1)
    else:
        break

### 查询店铺信息
activity_store_list_response = api.get_activity_store_list(activity_id=activity_id)
store_id = activity_store_list_response.json()['data']['list'][0]['storeId']
store_name = activity_store_list_response.json()['data']['list'][0]['storeName']

### 查询场次信息
session_id = None
activity_session_list_response = api.get_activity_session_list(activity_id=activity_id, store_id=store_id)
for session_detail in activity_session_list_response.json()['data']:
    if session_detail['sessionBeginTime'] == session_begin_time:
        session_id = session_detail['sessionId']
        break

### 开始预约
while True:
    try:
        appointment_response = api.appointment(activity_id=activity_id, store_id=store_id, store_name=store_name, session_id=session_id)
        logging.info(f'尝试预约，活动id：{activity_id}，店铺id：{store_id}，场次id：{session_id}')
        if appointment_response.status_code != 500 and appointment_response.json()['success']:
            break
    except Exception as e:
        logging.error(f'尝试预约失败，错误原因：{e.args}')
    finally:
        time.sleep(0.5)
