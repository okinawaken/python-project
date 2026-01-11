import logging

import requests

import config


class KlookApi:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://www.klook.cn'

    def manual_redeem(self, program_uuid):
        return self.session.post(
            url=f'{self.base_url}/v2/promosrv/program/manual_redeem',
            headers=config.get_headers(),
            json={
                'program_uuid': program_uuid
            }
        )
