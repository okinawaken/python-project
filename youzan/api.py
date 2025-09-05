import json
import logging

import requests

import config


class YouzanApi:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self):
        self.session = requests.Session()

    def goods_search(self, kdt_id, keyword):
        return self.session.get(
            url='https://h5.youzan.com/wscshop/showcase/goods_search/goods.json',
            params={
                'kdt_id': kdt_id,
                'keyword': keyword,
                'page': 1,
                'page_size': 20
            }
        )

    def goods_detail_v2(self, alias):
        return self.session.get(
            url='https://h5.youzan.com/wscgoods/tee-app/detail-v2.json',
            params={
                'alias': alias
            }
        )

    def get_address_list(self):
        return self.session.post(
            url='https://cashier.youzan.com/wsctrade/uic/address/getAddressList.json',
            headers=config.get_headers()
        )

    def get_default_self_fetch_address(self, kdt_id, goods_id, sku_id, num):
        return self.session.post(
            url='https://cashier.youzan.com/pay/wsctrade/order/buy/getDefaultSelfFetch.json',
            headers=config.get_headers(),
            json={
                'kdtId': kdt_id,
                'items': [
                    {
                        'goodsId': goods_id,
                        'skuId': sku_id,
                        'num': num,
                    }
                ],
                'page': 1,
                'pageSize': 20
            }
        )

    def get_self_fetch_address_list(self, kdt_id, goods_id, sku_id, num):
        return self.session.post(
            url='https://cashier.youzan.com/pay/wsctrade/order/buy/v2/getSelfFetchList.json',
            headers=config.get_headers(),
            json={
                'kdtId': kdt_id,
                'items': [{
                    'goodsId': goods_id,
                    'skuId': sku_id,
                    'num': num
                }],
                'page': 1,
                'pageSize': 20
            }
        )

    def goods_book(self, kdt_id, goods_id, sku_id, property_ids, num):
        return self.session.post(
            url='https://h5.youzan.com/wsctrade/order/goodsBook.json',
            headers=config.get_headers(),
            params=config.get_access_params(),
            data=json.dumps({
                'common': json.dumps({
                    'kdt_id': kdt_id,
                }),
                'goodsList': json.dumps([
                    {
                        'goods_id': goods_id,
                        'sku_id': sku_id,
                        'propertyIds': property_ids,
                        'num': num
                    }
                ])
            })
        )

    def prepare_by_book_key(self, book_key):
        return self.session.get(
            url='https://cashier.youzan.com/pay/wsctrade/order/buy/prepare-by-book-key.json',
            headers=config.get_headers(),
            params={
                'bookKey': book_key
            }
        )

    def order_buy(self, kdt_id, goods_id, sku_id, property_ids, num, delivery):
        return self.session.post(
            url='https://cashier.youzan.com/pay/wsctrade/order/buy/v2/bill-fast.json',
            headers=config.get_headers(),
            params=config.get_access_params(),
            json={
                'version': 2,
                'source': {},
                'config': {},
                'items': [
                    {
                        'kdtId': kdt_id,
                        'goodsId': goods_id,
                        'skuId': sku_id,
                        'propertyIds': property_ids,
                        'num': num
                    }
                ],
                'delivery': delivery
            }
        )
