import logging

import requests

import config


class MccApi:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://right-mc.bestdo.com'

    def get_mer_list(self, mer_type, city_id, page=1):
        return self.session.post(
            url=f'{self.base_url}/mer/ajaxMerList',
            headers=config.get_headers(),
            data={
                'type': mer_type,
                'city_id': city_id,
                'page': page,
            }
        )

    def get_mer_item_info(self, mer_item_id, mer_type):
        return self.session.get(
            url=f'{self.base_url}/item/info',
            headers=config.get_headers(),
            params={
                'mer_item_id': mer_item_id,
                'type': mer_type
            }
        )

    def get_valid_price_time(self, mer_item_id, date, ids):
        return self.session.post(
            url=f'{self.base_url}/item/ajaxGetValidPriceTime',
            headers=config.get_headers(),
            data={
                'mer_item_id': mer_item_id,
                'date': date,
                'ids': ids
            }
        )

    def create_order(self, mer_item_id, book_day, hour, mer_type, token):
        return self.session.get(
            url=f'{self.base_url}/order/createOrder',
            headers=config.get_headers(),
            params={
                'mer_item_id': mer_item_id,
                'book_day': book_day,
                'hour': hour,
                'type': mer_type,
                'token': token
            }
        )

    def create_sports_order(self, mer_id, mer_item_id, book_day, username, phone, hour, mer_type, price_time_id, post_key):
        return self.session.post(
            url=f'{self.base_url}/order/createSportsOrder',
            headers=config.get_headers(),
            data={
                'mer_id': mer_id,
                'mer_item_id': mer_item_id,
                'book_day': book_day,
                'username': username,
                'phone': phone,
                'hour': hour,
                'type': mer_type,
                'price_time_id': price_time_id,
                'post_key': post_key
            }
        )
