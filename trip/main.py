from InquirerPy import inquirer
from InquirerPy.base import Choice

from trip.api import TripApi

api = TripApi()

### 搜索演唱会
keyword = inquirer.text(
    message='请输入你想搜索的演唱会名称：'
).execute()
suggest_response = api.suggest(keyword=keyword)

### 选择演唱会
poi_detail = inquirer.select(
    message='请选择你想购买的演唱会：',
    choices=[
        Choice(name=f'{suggest_detail['poiInfo']['name']}', value=suggest_detail['poiInfo']) for suggest_detail in suggest_response.json()['suggestInfoList']
    ]
).execute()
product_shelf_to_show_contest_response = api.get_product_shelf_to_show_contest(poi_id=poi_detail['bizId'])

### 选择日期票档购买数量
date = None
for filter_condition in product_shelf_to_show_contest_response.json()['filterResult']['filters']:
    if filter_condition['type'] == 'DateFilter':
        date = inquirer.select(
            message='请选择你想购买的日期：',
            choices=[
                Choice(name=f'{filter_item['value']}', value=f'{filter_item['value']}') for filter_item in filter_condition['filterItems']
            ]
        ).execute()
resource = inquirer.select(
    message='请选择你想购买的票档：',
    choices=[
        Choice(name=f'{resource['name']}', value=resource) for resource in product_shelf_to_show_contest_response.json()['resources']
    ]
).execute()
count = inquirer.number(
    message='请输入你想购买的数量：',
    default=1
).execute()

bp_link = f'https://m.ctrip.com/webapp/tnt/booking?date={date}&selectDate={date}&count={count}&optid={resource['id']}&poiid={resource['poiId']}&spotid={resource["spotid"]}&token={resource['token']}'
print(f'最终生成的bp链接：{bp_link}')
