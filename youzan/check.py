import logging
import smtplib
import time
from email.mime.text import MIMEText

from InquirerPy import inquirer
from InquirerPy.base import Choice

from api import YouzanApi

api = YouzanApi()

### 通知信息
sender_smtp_address = inquirer.text(
    message='请输入发件人smtp邮箱地址：',
    default='smtp.163.com'
).execute()
sender_mail = inquirer.text(
    message='请输入发送人邮箱地址：',
    default='scbinghun@163.com'
).execute()
sender_password = inquirer.secret(
    message='请输入发送者邮箱密码：'
).execute()
receiver_mail = inquirer.text(
    message='请输入收件人邮箱地址：',
    default='1138700280@qq.com'
).execute()

### 搜索商品
kdt_id = inquirer.select(
    message='请选择你想要搜索的店铺：',
    choices=[
        Choice(value=140713009, name='店铺id：140713009 店铺名称：那家小铺'),
        Choice(value=164887806, name='店铺id：164887806，店铺名称：TinyRoll'),
        Choice(value=90605957, name='店铺id：90605957，店铺名称：Toris')
    ]
).execute()
keyword = inquirer.text(
    message='请输入你想要搜索的商品：'
).execute()
goods_search_response = api.goods_search(kdt_id=kdt_id, keyword=keyword)
goods_search_detail = inquirer.select(
    message='请选择你想购买的商品：',
    choices=[Choice(value=goods, name=f'商品id：{goods['id']} 商品标题：{goods['title']}') for goods in goods_search_response.json()['data']]
).execute()

### 查询商品详情信息
while True:
    try:
        goods_detail_v2_response = api.goods_detail_v2(alias=goods_search_detail['alias'])
        sold_status = goods_detail_v2_response.json()['data']['goodsData']['goods']['soldStatus']
        logging.info(f'持续监控商品中，当前状态：{sold_status}')
        if sold_status == 'SALE':
            mail_server = smtplib.SMTP(host=sender_smtp_address, port=25)
            mail_server.login(user=sender_mail, password=sender_password)
            mail_server.sendmail(from_addr=sender_mail, to_addrs=receiver_mail, msg=MIMEText(_text='你关注的商品上架了', _subtype='plain', _charset='utf-8').as_string())
            mail_server.quit()
    except Exception as e:
        logging.error(f'查询商品详情失败，错误原因：{e.args}')
    finally:
        time.sleep(60)
