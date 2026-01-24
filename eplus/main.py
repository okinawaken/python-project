import requests
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import json

# 第二张图的代码部分（数据获取）
detail = "4317710001-P0030001?P6=001&P1=0402&P59=1"

# 下载详情页面
response = requests.get(f"https://eplus.jp/sf/detail/{detail}")
html_content = response.text

# 提取 time_token
time_token_match = re.search(r'id="time_token"[^>]*value="([^"]*)"', html_content)
if time_token_match:
    time_token = time_token_match.group(1)
else:
    time_token = ""

# 提取 MainJSP1 URL
main_jsp_match = re.search(r"window\.location\.href='(https://sp\.atom\.eplus\.jp/sys/main\.jsp\?[^']*)'", html_content)
if main_jsp_match:
    main_jsp1 = main_jsp_match.group(1)
else:
    print("找不到指定的Url1")
    exit()

# 构造 DvcParam
# 从detail中提取前10位字符（兴行代码+巡演代码）
detail_code = detail.split('?')[0].split('-')[0]  # "4317710001"
kogyo_code = detail_code[:6]  # 前6位：兴行代码 "431771"
tour_code = detail_code[6:10]  # 后4位：巡演代码 "0001"

# 构造参数：{"0": "time_token,S4,kogyo_code,tour_code"}
dvc_param = json.dumps({"0": f"{time_token},S4,{kogyo_code},{tour_code}"})

# 获取 DvcId
params = {"params": dvc_param}
dvc_response = requests.get("https://eplus.jp/sf/dvcjudge", params=params)
dvc_id = dvc_response.text.replace('"', '')

# 第一张图的代码部分（浏览器初始化）
# 设置Chrome选项
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# 创建浏览器实例（自动管理ChromeDriver）
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 设置Cookie
driver.get("https://eplus.jp")
cookie = {
    'name': 'DVC_UNIQUE_ID',
    'value': dvc_id,
    'domain': '.eplus.jp',
    'path': '/'
}
driver.add_cookie(cookie)

# 加载主页面
driver.get(main_jsp1)

# 保持浏览器打开（等待用户操作）
input("按Enter键关闭浏览器...")
driver.quit()
