import logging

import requests

import config


class MinisoApi:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self):
        self.session = requests.Session()

    def get_activity_page_detail(self, activity_page_id):
        return self.session.get(
            url='https://api.multibrands.miniso.com/multi-configure-platform/api/page/detail',
            headers=config.get_headers(),
            params={
                'id': activity_page_id
            }
        )

    def get_activity_page_json(self, json_url):
        return self.session.get(
            url=json_url,
            headers=config.get_headers()
        )

    def get_activity_detail(self, activity_code):
        return self.session.get(
            url='https://api.multibrands.miniso.com/multi-configure-platform/api/activity/detail',
            headers=config.get_headers(),
            params={
                'code': activity_code
            }
        )

    def get_activity_store_list(self, activity_id):
        return self.session.post(
            url='https://cdn-storeexpress.miniso.com/reservation/storeInfo/list',
            headers=config.get_headers(),
            json={
                'pageNum': 1,
                'pageSize': 1,
                'activityId': activity_id
            }
        )

    def get_activity_session_list(self, activity_id, store_id):
        return self.session.post(
            url='https://api.multibrands.miniso.com/multi-configure-platform/api/activity/reservation/33611e56-bbb2-4e01-8bf5-8c71e99f0f40',
            headers=config.get_headers(),
            json={
                'activityId': activity_id,
                'storeIds': [
                    store_id
                ]
            }
        )

    def appointment(self, activity_id, store_id, store_name, session_id):
        return self.session.post(
            url='https://api.multibrands.miniso.com/multi-configure-platform/api/activity/reservation/34dfac98-7716-400d-861f-3ac705749bd6',
            headers=config.get_headers(),
            json={
                'activityId': activity_id,
                'storeId': store_id,
                'storeName': store_name,
                'sessionId': session_id,
                'memberId': 1236092285,
                'memberName': '王蕾锦',
                'memberPhone': '17683000617',
                "memberValue": ""
            }
        )
