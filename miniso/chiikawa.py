import logging
import time

import requests

import utils.time_utils as time_utils
import config

### 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

### 第一步，根据指定的日期去查询到二跳页面
date = time_utils.time_str_format(config.get_session_begin_time(), '%Y-%m-%d %H:%M:%S', '%Y-%m-%d')
page_response = requests.get(
    'https://api.multibrands.miniso.com/multi-configure-platform/api/page/detail',
    headers=config.get_headers(),
    params={
        'id': config.get_page_id(date)
    }
)
if not page_response.json()['success'] or page_response.json()['data'] is None:
    logging.error(f'【查询页面信息失败】，请检查输入的日期是否正确，返回结果：{page_response.text}')
    exit(-1)
second_jump_url = page_response.json()['data']['pageDetails']['jsonUrl']
logging.info(f'【查询页面信息成功】，二跳页面链接：{second_jump_url}')

### 第二步，根据二跳页面去查询到活动码
activity_code = None
second_jump_response = requests.get(
    second_jump_url,
    headers=config.get_headers()
)
for second_jump_detail in second_jump_response.json():
    if second_jump_detail['type'] == 'appointment':
        activity_code = second_jump_detail['data']['actId']
if activity_code is None:
    logging.error(f'【查询二跳页面信息失败】，请检查输入的日期是否正确，返回结果：{second_jump_response.text}')
    exit(-1)
logging.info(f'【查询二跳页面信息成功】，活动码：{activity_code}')

### 第三步，根据活动码去查询活动id、活动开始时间、活动结束时间
activity_detail_response = requests.get(
    'https://api.multibrands.miniso.com/multi-configure-platform/api/activity/detail',
    headers=config.get_headers(),
    params={
        'code': activity_code
    }
)
if not activity_detail_response.json()['success'] or activity_detail_response.json()['data'] is None:
    logging.info(f'【查询活动详情失败】，请检查输入的日期是否正确，返回结果：{activity_detail_response.text}')
    exit(0)
activity_id = str(activity_detail_response.json()['data']['id'])
activity_name = activity_detail_response.json()['data']['activityName']
activity_begin_time = activity_detail_response.json()['data']['activityBeginTime']
activity_end_time = activity_detail_response.json()['data']['activityEndTime']
logging.info(f'【查询活动详情成功】，活动id：{activity_id}，活动名称：{activity_name}，活动开始时间：{activity_begin_time}，活动结束时间：{activity_end_time}')

### 第四步，等待活动开始
while not config.debug():
    countdown = time_utils.time_str_to_timestamp(activity_begin_time, '%Y/%m/%d %H:%M:%S') - int(time.time())
    logging.info(f'【等待活动开始】，还有{countdown}秒')

    if 600 <= countdown:
        time.sleep(60)
    elif 60 <= countdown < 600:
        time.sleep(1)
    elif 1 <= countdown < 60:
        time.sleep(0.5)
    elif 0.1 <= countdown < 1:
        time.sleep(0.1)
    else:
        break
logging.info('【等待活动结束】，开始查询店铺信息')

### 第五步，查询店铺信息
store_id = None
store_name = None
while store_id is None:
    store_response = requests.post(
        'https://cdn-storeexpress.miniso.com/reservation/storeInfo/list',
        headers=config.get_headers(),
        json={
            'pageNum': 1,
            'pageSize': 1,
            'latitude': 31.331993027542612,
            'longitude': 121.44670146196526,
            'activityId': activity_id,
            'selectCanReservationStore': True,
        }
    )
    if store_response.json()['success'] and 'list' in store_response.json()['data']:
        store_id = store_response.json()['data']['list'][0]['storeId']
        store_name = store_response.json()['data']['list'][0]['storeName']
    else:
        logging.info(f'【查询店铺信息失败】，重新尝试获取，返回结果：{store_response.text}')
        time.sleep(0.1)
logging.info(f'【查询店铺信息成功】，店铺id：{store_id}，店铺名称：{store_name}')

### 第六步，查询场次信息
session_id = None
while session_id is None:
    session_response = requests.post(
        'https://api.multibrands.miniso.com/multi-configure-platform/api/activity/reservation/33611e56-bbb2-4e01-8bf5-8c71e99f0f40',
        headers=config.get_headers(),
        json={
            'activityId': activity_id,
            'storeIds': [
                store_id
            ]
        }
    )
    if session_response.json()['success'] and session_response.json()['data'] is not None:
        for session_detail in session_response.json()['data']:
            if session_detail['sessionBeginTime'] == config.get_session_begin_time():
                session_id = session_detail['sessionId']
    else:
        logging.info(f'【查询场次信息失败】，重新尝试获取，返回结果：{session_response.text}')
        time.sleep(0.1)
logging.info(f'【查询场次信息成功】，场次id：{session_id}')

### 第七步，开始抢票
while True:
    try:
        response = requests.post(
            'https://api.multibrands.miniso.com/multi-configure-platform/api/activity/reservation/34dfac98-7716-400d-861f-3ac705749bd6',
            headers=config.get_headers(),
            json={
                'activityId': activity_id,
                'storeId': store_id,
                'storeName': store_name,
                'sessionId': session_id,
                **config.get_member_info()
            }
        )
        logging.info(
            f'【尝试抢票】，活动id：{activity_id}，店铺id：{store_id}，场次id：{session_id}，个人信息：{config.get_member_info()}，返回结果：{response.text}'
        )
        if response.status_code != 500 and response.json()['success']:
            break
    except Exception as e:
        logging.error(f'【抢票失败】，错误原因：{e.args}')
    finally:
        time.sleep(0.3)
