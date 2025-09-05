import json

import encryption


def debug():
    return False


def get_headers():
    header_noice = encryption.get_noice()
    header_time = encryption.get_time()
    header_signature = encryption.get_signature(header_noice, header_time)
    with open('headers.json', 'r', encoding='utf-8') as f:
        headers = json.load(f)
    return {
        **headers,
        'nonce': header_noice,
        'time': header_time,
        'signature': header_signature
    }


def get_page_id(date):
    date_page_dict = {
        '2025-08-22': '6314',
        '2025-08-23': '6315',
        '2025-08-24': '6316',
        '2025-08-25': '6317'
    }
    return date_page_dict[date]


def get_session_begin_time():
    ### 0822场次 2025-08-22 10:00:00
    ### 0823场次 2025-08-23 10:00:00
    ### 0824场次 2025-08-24 10:00:00
    ### 0825场次 2025-08-25 10:00:00
    return '2025-08-25 10:00:00'


def get_member_info():
    member_id = get_headers()['content-uid']
    member_info_dict = {
        'memberId': member_id,
        'memberName': '周玉慧',
        'memberPhone': '13482188755',
        'memberValue': '',
    }
    return member_info_dict
