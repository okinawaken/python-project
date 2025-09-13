import logging

import requests


class TripApi:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self):
        self.session = requests.Session()

    def suggest(self, keyword):
        return self.session.post(
            url='https://m.ctrip.com/restapi/soa2/28485/json/suggestResult',
            json={
                'keyword': keyword,
                'head': {
                    'syscode': '09',
                    'extension': [
                        {
                            'name': 'gs_page_code',
                            'value': '10650102726',
                        },
                        {
                            'name': 'gs_activitybiz_source',
                            'value': 'gs_activitybiz_searchResult',
                        }
                    ]
                }
            }
        )

    def get_product_shelf_to_show_contest(self, poi_id):
        return self.session.post(
            url='https://m.ctrip.com/restapi/soa2/21052/getProductShelfToShowContest',
            json={
                'poiId': poi_id,
                'head': {
                    'syscode': '09'
                },
                "tags": [{
                    "key": "needProductActivity",
                    "value": "T"
                }, {
                    "key": "needShowContest",
                    "value": "T"
                }]
            }
        )
