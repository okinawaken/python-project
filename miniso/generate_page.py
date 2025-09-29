import json
import time

from InquirerPy import inquirer

import config
from api import MinisoApi

data = []
api = MinisoApi()

### 加载配置文件
config_path = inquirer.filepath(
    message='请输入你的配置文件路径：',
    default='config.json'
).execute()
config.load_config(config_path)

### 批量导入数据
for activity_page_id in range(6300, 6700):
    time.sleep(1)
    activity_page_detail_response = api.get_activity_page_detail(activity_page_id=activity_page_id)
    if activity_page_detail_response.json()['data'] and activity_page_detail_response.json()['data']['pageDetails'] and activity_page_detail_response.json()['data']['pageDetails']['jsonUrl']:
        json_url = activity_page_detail_response.json()['data']['pageDetails']['jsonUrl']
        activity_page_json_response = api.get_activity_page_json(json_url=json_url)
        for activity_page_detail in activity_page_json_response.json():
            if activity_page_detail['type'] == 'appointment':
                activity_id = activity_page_detail['data']['actId']
                data.append({
                    'page_id': activity_page_detail_response.json()['data']['id'],
                    'page_name': activity_page_detail_response.json()['data']['pageName'],
                    'activity_id': activity_id,
                })

with open('page.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
