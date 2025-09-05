import hashlib
import random
import time


def get_noice():
    e = '1234567890qwertyuiopasdfghjklzxc'
    return ''.join(e[random.randint(0, len(e) - 1)] for _ in range(len(e)))


def get_time():
    return str(int(time.time() * 1000))


def get_signature(noice, time):
    o = f'#storeexpress1.0#ffe232&t%4df!67sx55eas#{time}#{noice}'
    md5_hash = hashlib.md5(o.encode('utf-8')).hexdigest()
    return md5_hash.upper()
