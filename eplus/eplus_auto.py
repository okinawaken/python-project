#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eplus.jp 自动购票脚本 v2.1
- 用户需先在浏览器中登录 eplus 账号
- 脚本自动选择席位、支付方式、勾选确认框
- 最终购买按钮由用户决定是否点击（auto_confirm_purchase=false时）
- 使用 undetected-chromedriver 实现更好的反检测
"""

import os
import time
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass
from typing import Optional, List, Callable
from enum import Enum
from pathlib import Path

# 加载.env配置
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARN] python-dotenv未安装，无法读取.env文件")
    print("       pip install python-dotenv")

# 尝试导入undetected-chromedriver
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
    USE_UNDETECTED = True
    print("[INFO] 使用 undetected-chromedriver (反检测模式)")
except ImportError:
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
        USE_UNDETECTED = False
        print("[INFO] 使用 selenium (建议安装 undetected-chromedriver)")
    except ImportError:
        print("请安装依赖: pip install undetected-chromedriver python-dotenv")
        sys.exit(1)


class PaymentMethod(Enum):
    """支付方式枚举"""
    CREDIT_CARD = "クレジットカード"
    CONVENIENCE = "コンビニ"
    NET_BANKING = "ネットバンキング"


class TicketQuantityStrategy(Enum):
    """票数选择策略"""
    MAX = "max"
    MIN = "min"
    SPECIFIC = "specific"


@dataclass
class EplusConfig:
    """eplus配置类"""
    ticket_url: str
    username: str
    password: str
    chrome_path: str = ""
    mobile_ua: str = "Mozilla/5.0 (Linux; Android 14; 23116PN5BC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    payment_method: PaymentMethod = PaymentMethod.CONVENIENCE
    ticket_quantity_strategy: TicketQuantityStrategy = TicketQuantityStrategy.MAX
    ticket_quantity: int = 1
    wait_timeout: int = 10
    action_delay: float = 0.1
    auto_confirm_purchase: bool = False

    @classmethod
    def from_env(cls) -> 'EplusConfig':
        """从环境变量创建配置"""
        payment_map = {
            'CREDIT_CARD': PaymentMethod.CREDIT_CARD,
            'CONVENIENCE': PaymentMethod.CONVENIENCE,
            'NET_BANKING': PaymentMethod.NET_BANKING
        }
        strategy_map = {
            'MAX': TicketQuantityStrategy.MAX,
            'MIN': TicketQuantityStrategy.MIN,
            'SPECIFIC': TicketQuantityStrategy.SPECIFIC
        }

        return cls(
            ticket_url=os.getenv('TICKET_URL', ''),
            username=os.getenv('EPLUS_USERNAME', ''),
            password=os.getenv('EPLUS_PASSWORD', ''),
            chrome_path=os.getenv('CHROME_PATH', ''),
            mobile_ua=os.getenv('MOBILE_UA', cls.mobile_ua),
            payment_method=payment_map.get(os.getenv('PAYMENT_METHOD', 'CONVENIENCE'), PaymentMethod.CONVENIENCE),
            ticket_quantity_strategy=strategy_map.get(os.getenv('TICKET_QUANTITY_STRATEGY', 'MAX'), TicketQuantityStrategy.MAX),
            ticket_quantity=int(os.getenv('TICKET_QUANTITY', '1')),
            wait_timeout=int(os.getenv('WAIT_TIMEOUT', '10')),
            action_delay=float(os.getenv('ACTION_DELAY', '0.5')),
            auto_confirm_purchase=os.getenv('AUTO_CONFIRM_PURCHASE', 'false').lower() == 'true'
        )


class EplusAutomation:
    """eplus自动化购票类 - 泛用版"""

    def __init__(self, config: EplusConfig):
        self.config = config
        self.driver = None
        self.wait: Optional[WebDriverWait] = None
        self.log_callback: Optional[Callable[[str], None]] = None  # GUI日志回调

    def log(self, message: str):
        """输出日志"""
        print(message)
        if self.log_callback:
            self.log_callback(message)

    def setup_driver(self):
        """设置Chrome驱动 - 使用undetected_chromedriver（自动处理版本匹配）"""
        # 获取程序运行目录
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
        else:
            app_dir = Path(__file__).parent

        # Chrome路径和参数
        chrome_path = self.config.chrome_path or str(app_dir / "chrome-win" / "chrome.exe")
        user_agent = self.config.mobile_ua

        # 使用固定的用户数据目录
        user_data_dir = str(app_dir / "chrome_profile")

        self.log(f"[INFO] 启动Chrome: {chrome_path}")
        print(f"[INFO] 用户数据目录: {user_data_dir}")
        print(f"[INFO] User-Agent: {user_agent[:50]}...")

        if USE_UNDETECTED:
            print("[INFO] 初始化undetected_chromedriver...")
            print("[INFO] 如果卡住，可能是在下载chromedriver，请等待...")

            options = uc.ChromeOptions()
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--no-first-run')  # 禁止首次运行向导
            options.add_argument('--no-default-browser-check')  # 禁止默认浏览器检查
            options.add_argument('--disable-session-crashed-bubble')  # 禁止会话恢复提示
            options.binary_location = chrome_path

            # undetected_chromedriver会自动下载匹配的chromedriver
            # 由于使用自定义Chrome路径，需要手动指定版本
            print("[INFO] 正在启动Chrome（首次运行会下载chromedriver）...")
            self.driver = uc.Chrome(
                options=options,
                version_main=146,  # 手动指定Chrome版本，因为自定义路径无法自动检测
                use_subprocess=True  # 使用子进程模式
            )
            print("[INFO] Chrome启动成功")
        else:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions

            options = ChromeOptions()
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--no-first-run')  # 禁止首次运行向导
            options.add_argument('--no-default-browser-check')  # 禁止默认浏览器检查
            options.add_argument('--disable-session-crashed-bubble')  # 禁止会话恢复提示
            options.binary_location = chrome_path
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])

            self.driver = webdriver.Chrome(options=options)

        # 打开票务页面
        print(f"[INFO] 正在打开票务页面...")
        self.driver.get(self.config.ticket_url)
        print(f"[INFO] 已打开页面: {self.driver.current_url}")

        self.wait = WebDriverWait(self.driver, self.config.wait_timeout)
        print("[INFO] Chrome驱动已启动")

    def delay(self, seconds: float = None):
        """延迟操作"""
        time.sleep(seconds or self.config.action_delay)

    def wait_for_page_change(self, current_url: str, timeout: int = 10):
        """等待页面URL变化"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.current_url != current_url
            )
        except TimeoutException:
            pass  # 超时则继续

    def wait_for_element_gone(self, element, timeout: int = 5):
        """等待元素消失（页面刷新后元素会失效）"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.staleness_of(element))
        except TimeoutException:
            pass

    def wait_for_element_appear(self, by: By, value: str, timeout: int = 60, poll: float = 0.1):
        """等待元素出现（用于抢票时等待按钮出现）"""
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=poll).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None

    def wait_for_clickable(self, by: By, value: str, timeout: int = 60, poll: float = 0.1):
        """等待元素可点击（poll_frequency=0.1秒，每100ms检测一次）"""
        try:
            return WebDriverWait(self.driver, timeout, poll_frequency=poll).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            return None

    # ==================== 通用元素查找方法 ====================

    def find_element_by_text(self, tag: str, text: str, exact: bool = False) -> Optional[any]:
        """通过文本内容查找元素"""
        try:
            elements = self.driver.find_elements(By.TAG_NAME, tag)
            for elem in elements:
                elem_text = elem.text.strip()
                if exact:
                    if elem_text == text:
                        return elem
                else:
                    if text in elem_text:
                        return elem
        except StaleElementReferenceException:
            pass
        return None

    def find_elements_by_text(self, tag: str, text: str, exact: bool = False) -> List:
        """通过文本内容查找所有匹配元素"""
        result = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, tag)
            for elem in elements:
                elem_text = elem.text.strip()
                if exact:
                    if elem_text == text:
                        result.append(elem)
                else:
                    if text in elem_text:
                        result.append(elem)
        except StaleElementReferenceException:
            pass
        return result

    def find_clickable_by_text(self, text: str, exact: bool = False) -> Optional[any]:
        """查找可点击元素（按钮、链接等）"""
        for tag in ['button', 'a', 'input[type="submit"]', 'input[type="button"]']:
            elem = self.find_element_by_text(tag.split('[')[0], text, exact)
            if elem:
                return elem
        # 尝试通过XPath查找包含文本的可点击元素
        try:
            xpath = f"//*[contains(text(), '{text}') and (self::a or self::button)]"
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements:
                return elements[0]
        except:
            pass
        return None

    def find_input_by_label(self, label_text: str) -> Optional[any]:
        """通过label文本查找对应的input"""
        try:
            # 方法1: 通过label的for属性
            labels = self.driver.find_elements(By.TAG_NAME, 'label')
            for label in labels:
                if label_text in label.text:
                    for_id = label.get_attribute('for')
                    if for_id:
                        try:
                            return self.driver.find_element(By.ID, for_id)
                        except:
                            pass
                    # 方法2: label内部的input
                    try:
                        return label.find_element(By.TAG_NAME, 'input')
                    except:
                        pass
        except:
            pass
        return None

    def find_radio_by_label(self, label_text: str) -> Optional[any]:
        """通过label文本查找单选框"""
        try:
            # 查找包含指定文本的label，然后找其关联的radio
            xpath = f"//label[contains(text(), '{label_text}')]//input[@type='radio'] | //label[contains(text(), '{label_text}')]/preceding-sibling::input[@type='radio'] | //input[@type='radio']/following-sibling::label[contains(text(), '{label_text}')]/../input[@type='radio']"
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements:
                return elements[0]

            # 备用方法：遍历所有radio的父元素
            radios = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            for radio in radios:
                parent = radio.find_element(By.XPATH, '..')
                if label_text in parent.text:
                    return radio
        except:
            pass
        return None

    def safe_click(self, element):
        """安全点击元素"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.delay(0.2)
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def select_first_valid_option(self, select_element) -> bool:
        """选择有效选项 - 优先选择第二个，其次选择第一个"""
        try:
            select = Select(select_element)
            valid_options = []
            skip_texts = ['-----', '選択して下さい', '選択してください', '---']

            # 收集所有有效选项
            for opt in select.options:
                value = opt.get_attribute('value')
                text = opt.text.strip()
                # 跳过空值和占位符
                if value and value.strip() and not value.startswith('　') and text not in skip_texts:
                    valid_options.append((value, text))

            if len(valid_options) == 0:
                print("[WARN] 没有找到有效选项")
                return False

            # 优先选择第二个有效选项，如果没有则选择第一个
            if len(valid_options) >= 2:
                target_value, target_text = valid_options[1]  # 第二个选项
                print(f"[INFO] 选择第二个选项: {target_text}")
            else:
                target_value, target_text = valid_options[0]  # 第一个选项
                print(f"[INFO] 只有一个选项，选择: {target_text}")

            select.select_by_value(target_value)
            self.trigger_change(select_element)
            return True
        except Exception as e:
            print(f"[WARN] 选择失败: {e}")
        return False

    def select_max_quantity(self, select_element) -> bool:
        """选择最大数量"""
        try:
            select = Select(select_element)
            max_value = -1
            max_option = None
            for opt in select.options:
                value = opt.get_attribute('value')
                if value:
                    match = re.search(r'(\d+)$', value)
                    if match:
                        num = int(match.group(1))
                        if num > max_value:
                            max_value = num
                            max_option = opt
            if max_option:
                select.select_by_value(max_option.get_attribute('value'))
                print(f"[INFO] 选择最大票数: {max_value}")
                self.trigger_change(select_element)
                return True
        except Exception as e:
            print(f"[WARN] 选择最大数量失败: {e}")
        return False

    def select_specific_quantity(self, select_element, quantity: int) -> bool:
        """选择指定数量"""
        try:
            select = Select(select_element)
            for opt in select.options:
                value = opt.get_attribute('value')
                text = opt.text.strip()
                if value and (f'/{quantity}' in value or text == str(quantity) or text.startswith(f'{quantity}枚')):
                    select.select_by_value(value)
                    print(f"[INFO] 选择票数: {quantity}")
                    self.trigger_change(select_element)
                    return True
        except Exception as e:
            print(f"[WARN] 选择指定数量失败: {e}")
        return False

    def trigger_change(self, element):
        """触发change事件"""
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            element
        )

    # ==================== 页面处理方法 ====================

    def handle_ticket_detail_page(self):
        """处理票务详情页 - 使用MutationObserver实现事件驱动

        处理三种情况：
        1. 页面需要刷新才出现按钮
        2. 灰色按钮（disabled）变成可点击
        3. 用户主动刷新页面
        """
        print("[INFO] 处理票务详情页...")

        # 注入MutationObserver脚本，监听按钮出现和属性变化
        js_observer = """
        (function() {
            // 重置状态（支持页面刷新后重新注入）
            window._eplusButtonClicked = false;
            window._eplusObserverRunning = true;

            function clickButton() {
                // 检查 #order-button（必须没有disabled属性）
                var btn = document.querySelector('#order-button');
                if (btn && !btn.disabled && !btn.hasAttribute('disabled')) {
                    console.log('[MutationObserver] 找到可点击的 #order-button，点击');
                    btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                    window._eplusButtonClicked = true;
                    return true;
                }

                // 检查 button.button--primary（必须没有disabled属性）
                var buttons = document.querySelectorAll('button.button--primary');
                for (var i = 0; i < buttons.length; i++) {
                    var b = buttons[i];
                    if (b.textContent.includes('次') && !b.disabled && !b.hasAttribute('disabled')) {
                        console.log('[MutationObserver] 找到可点击的 button--primary，点击');
                        b.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        window._eplusButtonClicked = true;
                        return true;
                    }
                }
                return false;
            }

            // 先尝试点击一次
            if (clickButton()) return 'clicked';

            // 设置MutationObserver监听DOM变化和属性变化
            var observer = new MutationObserver(function(mutations) {
                if (clickButton()) {
                    observer.disconnect();
                    window._eplusObserverRunning = false;
                }
            });

            observer.observe(document.body, {
                childList: true,      // 监听子元素变化（按钮出现）
                subtree: true,        // 监听所有后代
                attributes: true,     // 监听属性变化（disabled被移除）
                attributeFilter: ['disabled', 'class']  // 只监听这些属性
            });

            // 5分钟后自动停止
            setTimeout(function() {
                observer.disconnect();
                window._eplusObserverRunning = false;
            }, 300000);

            return 'observer_started';
        })();
        """

        # 等待按钮被点击（最多5分钟）
        print("[INFO] 注入MutationObserver，等待按钮出现...")
        start_time = time.time()
        last_url = self.driver.current_url
        last_inject_time = 0

        while time.time() - start_time < 300:
            current_url = self.driver.current_url

            # 检测页面是否刷新（URL变化或需要重新注入）
            need_reinject = False
            if current_url != last_url:
                print(f"[INFO] 检测到页面变化: {current_url}")
                # URL变化可能是跳转成功，检查是否还在detail页面
                if 'eplus.jp/sf/detail/' not in current_url:
                    print("[INFO] 页面已跳转，退出等待")
                    return
                last_url = current_url
                need_reinject = True

            # 每5秒重新注入一次（防止页面刷新后observer失效）
            if time.time() - last_inject_time > 5:
                need_reinject = True

            if need_reinject:
                try:
                    result = self.driver.execute_script(js_observer)
                    last_inject_time = time.time()
                    if result == 'clicked':
                        print("[INFO] 按钮已点击，等待页面跳转...")
                        self.wait_for_page_change(current_url, timeout=10)
                        return
                except Exception:
                    # 页面可能正在加载，忽略错误
                    pass

            # 检查是否已点击
            try:
                clicked = self.driver.execute_script("return window._eplusButtonClicked || false;")
                if clicked:
                    print("[INFO] MutationObserver已点击按钮")
                    self.wait_for_page_change(current_url, timeout=10)
                    return
            except:
                pass

            time.sleep(0.1)  # 100ms检查一次状态

        print("[WARN] 等待超时（5分钟），未找到可点击的'次へ'按钮")

    def handle_ticket_selection_page(self):
        """处理选票页面 - 快速版"""
        print("[INFO] 处理选票页面...")

        # 获取所有select元素
        selects = self.driver.find_elements(By.TAG_NAME, 'select')

        for select_elem in selects:
            try:
                select = Select(select_elem)
                options_text = ' '.join([opt.text for opt in select.options])

                if '枚' in options_text:
                    # 票数选择框
                    if self.config.ticket_quantity_strategy == TicketQuantityStrategy.MAX:
                        self.select_max_quantity(select_elem)
                    elif self.config.ticket_quantity_strategy == TicketQuantityStrategy.MIN:
                        self.select_specific_quantity(select_elem, 1)
                    else:
                        # 尝试选择指定数量，如果失败则选择最大可用数量
                        if not self.select_specific_quantity(select_elem, self.config.ticket_quantity):
                            print(f"[WARN] 无法选择{self.config.ticket_quantity}张票，尝试选择最大可用数量")
                            self.select_max_quantity(select_elem)
                else:
                    # 其他下拉框（公演日時、席種等）
                    self.select_first_valid_option(select_elem)
            except StaleElementReferenceException:
                pass
            except Exception as e:
                print(f"[WARN] 处理下拉框失败: {e}")

        # 点击登录链接
        login_link = self.find_clickable_by_text('ログイン画面へ')
        if login_link:
            print("[INFO] 点击'ログイン画面へ'")
            self.safe_click(login_link)
        else:
            # 备用：查找包含"ログイン"的链接
            login_link = self.find_clickable_by_text('ログイン')
            if login_link:
                print("[INFO] 点击登录链接")
                self.safe_click(login_link)

    def handle_login_page(self):
        """处理登录页面 - 泛用版"""
        print("[INFO] 处理登录页面...")

        # 查找用户名输入框
        username_input = None
        for selector in ['#loginId', 'input[name="loginId"]', 'input[type="email"]', 'input[name="email"]']:
            try:
                username_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                pass

        if not username_input:
            username_input = self.find_input_by_label('メールアドレス') or self.find_input_by_label('ID')

        if username_input:
            username_input.clear()
            username_input.send_keys(self.config.username)
            print(f"[INFO] 输入用户名: {self.config.username}")

        # 查找密码输入框
        password_input = None
        for selector in ['#loginPassword', 'input[name="loginPassword"]', 'input[type="password"]']:
            try:
                password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                pass

        if password_input:
            password_input.clear()
            password_input.send_keys(self.config.password)
            print("[INFO] 输入密码: ******")

        # 点击登录按钮
        login_btn = None
        for selector in ['#idPwLogin', 'button[type="submit"]', 'input[type="submit"]']:
            try:
                login_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                pass

        if not login_btn:
            login_btn = self.find_clickable_by_text('ログイン')

        if login_btn:
            current_url = self.driver.current_url
            self.safe_click(login_btn)
            print("[INFO] 点击登录按钮")
            self.wait_for_page_change(current_url)  # 等待页面跳转

    def handle_payment_page(self):
        """处理支付方式选择页面 - 使用JS直接操作单选框"""
        print("[INFO] 处理支付方式选择页面...")

        # 检查是否有iframe并切换
        switched_to_iframe = False
        iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    radios_in_iframe = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                    if radios_in_iframe:
                        switched_to_iframe = True
                        break
                    else:
                        self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()

        # 使用JS获取所有单选框并根据label文本选择
        payment_map = {
            PaymentMethod.CREDIT_CARD: 'クレジット',
            PaymentMethod.CONVENIENCE: 'コンビニ',
            PaymentMethod.NET_BANKING: 'ネットバンキング'
        }
        payment_keyword = payment_map.get(self.config.payment_method, 'コンビニ')

        # JS脚本：遍历所有radio，根据关联label的文本选择
        js_select_radios = f"""
        (function() {{
            var radios = document.querySelectorAll('input[type="radio"]');
            var selected = {{}};

            radios.forEach(function(radio) {{
                // 获取关联的label文本
                var labelText = '';
                if (radio.labels && radio.labels.length > 0) {{
                    labelText = radio.labels[0].textContent;
                }} else {{
                    var parent = radio.parentElement;
                    if (parent) labelText = parent.textContent;
                }}

                // 选择受取方法：优先スマチケ
                if (labelText.includes('スマチケ') && !selected['delivery']) {{
                    radio.checked = true;
                    radio.click();
                    radio.dispatchEvent(new Event('change', {{bubbles: true}}));
                    selected['delivery'] = 'スマチケ';
                }}

                // 选择支付方式
                if (labelText.includes('{payment_keyword}') && !selected['payment']) {{
                    radio.checked = true;
                    radio.click();
                    radio.dispatchEvent(new Event('change', {{bubbles: true}}));
                    selected['payment'] = '{payment_keyword}';
                }}
            }});

            return selected;
        }})();
        """

        try:
            result = self.driver.execute_script(js_select_radios)
            if result and result.get('delivery'):
                print(f"[INFO] 选择受取方法: {result['delivery']}")
            if result and result.get('payment'):
                print(f"[INFO] 选择支付方式: {result['payment']}")
            if not result or (not result.get('delivery') and not result.get('payment')):
                self._fallback_select_payment()
            # 等待页面响应radio选择
            self.delay(0.5)
        except Exception as e:
            print(f"[WARN] JS选择单选框失败: {e}")
            self._fallback_select_payment()
            self.delay(0.5)

        # 点击"次へ"
        next_link = self.find_clickable_by_text('次へ', exact=True)
        if next_link:
            current_url = self.driver.current_url
            self.safe_click(next_link)
            print("[INFO] 点击'次へ'")
            self.wait_for_page_change(current_url)
        else:
            for text in ['次へ進む', '確認', '進む']:
                btn = self.find_clickable_by_text(text)
                if btn:
                    current_url = self.driver.current_url
                    self.safe_click(btn)
                    print(f"[INFO] 点击'{text}'")
                    self.wait_for_page_change(current_url)
                    break

        # 如果之前切换到了iframe，切换回默认内容
        if switched_to_iframe:
            self.driver.switch_to.default_content()

    def _fallback_select_payment(self):
        """备用方法：使用原来的方式选择支付"""
        delivery_options = ['スマチケ', 'Cloakで届く', '配送']
        for option in delivery_options:
            radio = self.find_radio_by_label(option)
            if radio:
                self.safe_click(radio)
                print(f"[INFO] 选择受取方法: {option}")
                break

        payment_text = self.config.payment_method.value
        payment_radio = self.find_radio_by_label(payment_text)
        if payment_radio:
            self.safe_click(payment_radio)
            print(f"[INFO] 选择支付方式: {payment_text}")

    def handle_confirmation_page(self) -> bool:
        """处理确认购买页面 - 区分第一个和第二个确认界面

        返回值:
            True: 第一个确认界面，已点击申込み，需要继续循环
            False: 第二个确认界面，已勾选checkbox，等待用户确认
        """
        print("[INFO] 处理确认购买页面...")

        page_source = self.driver.page_source

        # 检查是否有checkbox来区分两个确认界面
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')

        # 通过页面特征来区分两个确认界面
        # 第一个确认界面：有"支払・受取方法を変更する"链接，没有checkbox
        # 第二个确认界面：有"申込み完了前注意事項"，有checkbox，有"同意して購入"按钮
        is_final_confirmation = '申込み完了前注意事項' in page_source or '同意して購入' in page_source or len(checkboxes) > 0

        if is_final_confirmation:
            # 第二个确认界面 - 有checkbox需要勾选
            print("[INFO] 检测到最终确认页面（第二个确认界面）")

            # 重新获取checkbox（页面可能已更新）
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            print(f"[DEBUG] 找到 {len(checkboxes)} 个checkbox")

            # 方法1：使用Selenium直接点击每个checkbox
            checked_count = 0
            for i, cb in enumerate(checkboxes):
                try:
                    # 滚动到元素可见
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb)
                    self.delay(0.1)

                    if not cb.is_selected():
                        # 尝试点击label（如果有的话）
                        try:
                            cb_id = cb.get_attribute('id')
                            if cb_id:
                                label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{cb_id}"]')
                                label.click()
                                print(f"[DEBUG] 点击label勾选checkbox {i+1}")
                                checked_count += 1
                                continue
                        except:
                            pass

                        # 直接点击checkbox
                        try:
                            cb.click()
                            print(f"[DEBUG] 直接点击勾选checkbox {i+1}")
                            checked_count += 1
                        except:
                            # JS点击
                            self.driver.execute_script("arguments[0].click();", cb)
                            print(f"[DEBUG] JS点击勾选checkbox {i+1}")
                            checked_count += 1
                except Exception as e:
                    print(f"[WARN] 勾选checkbox {i+1} 失败: {e}")

            print(f"[INFO] 共勾选 {checked_count} 个确认框")

            # 不自动点击购买按钮，等待用户决定
            if self.config.auto_confirm_purchase:
                return self.click_purchase_button()

            print("[INFO] 已勾选所有确认框，等待手动点击购买按钮")
            return False  # 返回False表示停止循环
        else:
            # 第一个确认界面 - 没有checkbox，需要点击"申込み"按钮
            print("[INFO] 检测到第一个确认页面，点击'申込み'进入最终确认")

            # 查找并点击"申込み"按钮
            apply_btn = self.find_clickable_by_text('申込み', exact=True)
            if apply_btn:
                current_url = self.driver.current_url
                self.safe_click(apply_btn)
                print("[INFO] 点击'申込み'按钮")
                self.wait_for_page_change(current_url)
                return True  # 返回True表示继续循环
            else:
                # 备用：查找其他可能的按钮
                for text in ['申込む', '次へ', '確認']:
                    btn = self.find_clickable_by_text(text)
                    if btn:
                        current_url = self.driver.current_url
                        self.safe_click(btn)
                        print(f"[INFO] 点击'{text}'按钮")
                        self.wait_for_page_change(current_url)
                        return True

            print("[WARN] 未找到申込み按钮")
            return False

    def click_purchase_button(self) -> bool:
        """点击最终购买按钮 - 真正锁票"""
        print("[INFO] 点击购买按钮...")
        purchase_keywords = ['同意して購入', '購入する', '申込み', '申し込む', '確定']
        for keyword in purchase_keywords:
            btn = self.find_clickable_by_text(keyword)
            if btn:
                self.safe_click(btn)
                print(f"[SUCCESS] 点击'{keyword}'按钮 - 锁票！")
                return True
        print("[WARN] 未找到购买按钮")
        return False

    def handle_post_login_redirect(self):
        """处理登录后的中间页面 - 直接点击次へ跳过"""
        print("[INFO] 处理登录后中间页面...")

        # 直接点击"次へ"按钮跳过
        next_btn = self.find_clickable_by_text('次へ')
        if next_btn:
            current_url = self.driver.current_url
            self.safe_click(next_btn)
            print("[INFO] 点击'次へ'跳过中间页面")
            self.wait_for_page_change(current_url)
        else:
            # 备用：查找任何可点击的确认按钮
            for text in ['確認', '進む', 'OK']:
                btn = self.find_clickable_by_text(text)
                if btn:
                    current_url = self.driver.current_url
                    self.safe_click(btn)
                    print(f"[INFO] 点击'{text}'跳过中间页面")
                    self.wait_for_page_change(current_url)
                    break

    def handle_auto_redirect(self):
        """处理自动跳转页面 - 等待或点击跳转链接"""
        print("[INFO] 检测到自动跳转页面，等待跳转...")
        current_url = self.driver.current_url

        # 尝试点击"こちら"链接加速跳转
        try:
            link = self.find_clickable_by_text('こちら')
            if link:
                self.safe_click(link)
                print("[INFO] 点击'こちら'加速跳转")
        except:
            pass
        # 等待页面跳转
        self.wait_for_page_change(current_url)

    def handle_email_verification_page(self):
        """处理邮箱验证页面 - 需要用户手动输入验证码"""
        print("\n" + "="*50)
        print("[WARN] 检测到邮箱验证页面！")
        print("eplus检测到可疑行为，需要输入邮箱验证码")
        print("请查看邮箱中的6位验证码")
        print("="*50)

        # 等待用户输入验证码
        code = input("\n请输入6位验证码（输入后按Enter继续）: ").strip()

        if len(code) == 6 and code.isdigit():
            # 查找验证码输入框
            try:
                code_input = None
                for selector in ['input[type="text"]', 'input[type="number"]', 'input[name*="code"]', 'input[placeholder*="認証"]']:
                    try:
                        inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for inp in inputs:
                            if inp.is_displayed():
                                code_input = inp
                                break
                        if code_input:
                            break
                    except:
                        pass

                if code_input:
                    code_input.clear()
                    code_input.send_keys(code)
                    print(f"[INFO] 输入验证码: {code}")

                    # 点击确认/次へ/登録按钮
                    next_btn = self.find_clickable_by_text('登録') or self.find_clickable_by_text('次へ') or self.find_clickable_by_text('確認') or self.find_clickable_by_text('送信')
                    if next_btn:
                        self.safe_click(next_btn)
                        print("[INFO] 点击确认按钮")
                else:
                    print("[WARN] 未找到验证码输入框，请手动输入")
            except Exception as e:
                print(f"[WARN] 输入验证码失败: {e}")
        else:
            print("[WARN] 验证码格式不正确，请手动完成验证")

    # ==================== 页面检测 ====================

    def detect_current_page(self) -> str:
        """检测当前页面类型 - 泛用版"""
        url = self.driver.current_url
        page_source = self.driver.page_source

        # 调试输出
        print(f"[DEBUG] 当前URL: {url}")

        # 基于URL判断
        if 'eplus.jp/sf/detail/' in url:
            return 'ticket_detail'

        # 检查自动跳转页面（优先于登录页面检测）
        if '自動的に遷移' in page_source:
            return 'auto_redirect'

        # 登录页面检测 - 必须有登录表单
        if 'member.eplus.jp/auth' in url or '/login' in url.lower():
            # 确认是真正的登录页面（有输入框）
            if 'loginId' in page_source or 'loginPassword' in page_source or 'type="password"' in page_source:
                return 'login'
            # 否则可能是跳转页面，等待自动跳转
            return 'auto_redirect'

        # 检查邮箱验证页面（追加认证）
        if 'メールアドレス認証' in page_source or '認証コード' in page_source:
            return 'email_verification'

        # 检查是否有错误/售罄提示
        error_keywords = ['受付期間外', '販売終了', '売り切れ', '完売', '申込受付は終了']
        for keyword in error_keywords:
            if keyword in page_source:
                print(f"[WARN] 检测到: {keyword}")
                return 'error'

        # 检查确认页面（优先级最高）
        if '申込み内容確認' in page_source or '購入内容確認' in page_source:
            return 'confirmation'
        if '今回の支払方法／受取方法' in page_source and '申込み' in page_source:
            return 'confirmation'

        # 检查选票页面（优先级高于支付页面）
        # "ログイン画面へ"按钮是选票页面的明确标识
        if 'ログイン画面へ' in page_source:
            return 'ticket_selection'
        # 有公演日時、席種、枚数下拉框的也是选票页面
        if '公演日時' in page_source and '席種' in page_source and '枚数' in page_source:
            return 'ticket_selection'

        # 检查支付页面（在选票页面之后检查）
        if '支払方法／受取方法の設定' in page_source:
            return 'payment'
        if '受取方法' in page_source and '支払方法' in page_source:
            return 'payment'

        # 检查登录后的中间页面 - 放在支付页面检测之后
        if 'afterLogin' in url or 'ShinKaiinJohoBean' in url:
            return 'post_login_redirect'

        # 完成页面 - 只在标题中检查，且要更严格
        if '<title>' in page_source:
            title_match = re.search(r'<title>([^<]+)</title>', page_source)
            if title_match:
                title = title_match.group(1)
                if '申込完了' in title or '購入完了' in title:
                    return 'complete'

        # 基于URL的atom/gesicht判断
        if 'atom.eplus.jp' in url or 'gesicht.eplus.jp' in url:
            if '支払' in page_source or '受取' in page_source:
                return 'payment'
            return 'ticket_selection'

        return 'unknown'

    # ==================== 主流程 ====================

    def run(self):
        """运行自动化流程"""
        try:
            self.setup_driver()
            # Chrome启动时已经打开了ticket_url，不需要再次导航

            max_iterations = 30
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                page_type = self.detect_current_page()
                print(f"\n[INFO] 当前页面类型: {page_type} (迭代 {iteration})")

                if page_type == 'ticket_detail':
                    self.handle_ticket_detail_page()
                elif page_type == 'ticket_selection':
                    self.handle_ticket_selection_page()
                elif page_type == 'login':
                    self.handle_login_page()
                elif page_type == 'post_login_redirect':
                    self.handle_post_login_redirect()
                elif page_type == 'auto_redirect':
                    self.handle_auto_redirect()
                elif page_type == 'email_verification':
                    self.handle_email_verification_page()
                elif page_type == 'payment':
                    self.handle_payment_page()
                elif page_type == 'confirmation':
                    should_continue = self.handle_confirmation_page()
                    if not should_continue:
                        # 已到达最终确认页面
                        if not self.config.auto_confirm_purchase:
                            print("\n[SUCCESS] 已到达最终确认页面，等待手动点击购买按钮...")
                            break
                    # 如果should_continue为True，继续循环处理下一个页面
                elif page_type == 'complete':
                    print("\n[SUCCESS] 购票完成！")
                    break
                elif page_type == 'error':
                    print("\n[ERROR] 票务不可用（售罄/不在销售期/错误）")
                    break
                else:
                    print(f"[WARN] 未知页面类型，等待...")

            print("\n[INFO] 自动化流程结束")

            # GUI模式下不自动关闭浏览器，让用户手动操作
            if self.log_callback:
                self.log("[INFO] 浏览器保持打开，请手动完成剩余操作")
                # 不关闭浏览器，等待用户手动关闭或点击停止按钮
                return
            else:
                # 命令行模式下等待用户按Enter
                input("按Enter键关闭浏览器...")

        except Exception as e:
            print(f"[ERROR] 发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 只在非GUI模式下自动关闭浏览器
            if self.driver and not self.log_callback:
                self.driver.quit()


def main():
    """主函数 - 从.env读取配置"""
    config = EplusConfig.from_env()

    if not config.ticket_url:
        print("[ERROR] 请在.env文件中设置TICKET_URL")
        sys.exit(1)

    if not config.username or not config.password:
        print("[ERROR] 请在.env文件中设置EPLUS_USERNAME和EPLUS_PASSWORD")
        sys.exit(1)

    print(f"[INFO] 票务URL: {config.ticket_url}")
    print(f"[INFO] 用户名: {config.username}")
    print(f"[INFO] 支付方式: {config.payment_method.value}")
    print(f"[INFO] 票数策略: {config.ticket_quantity_strategy.value}")

    automation = EplusAutomation(config)
    automation.run()


if __name__ == '__main__':
    main()
