#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eplus.jp 自动购票工具 - GUI版本
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

# 获取程序运行目录
if getattr(sys, 'frozen', False):
    # PyInstaller打包后的路径
    BASE_DIR = Path(sys._MEIPASS)  # 打包资源目录
    APP_DIR = Path(sys.executable).parent  # exe所在目录
else:
    BASE_DIR = Path(__file__).parent
    APP_DIR = BASE_DIR

# 设置Chrome路径（打包后Chrome在BASE_DIR，用户数据在APP_DIR）
CHROME_PATH = BASE_DIR / "chrome-win" / "chrome.exe"
CHROME_PROFILE = APP_DIR / "chrome_profile"


class EplusGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("eplus.jp 自动购票工具 v2.1")
        self.root.geometry("600x700")
        self.root.resizable(True, True)

        self.automation = None
        self.running = False

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ========== 票务URL ==========
        url_frame = ttk.LabelFrame(main_frame, text="票务URL", padding="5")
        url_frame.pack(fill=tk.X, pady=5)

        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        url_entry.pack(fill=tk.X, padx=5, pady=5)

        # ========== 登录信息 ==========
        login_frame = ttk.LabelFrame(main_frame, text="登录信息", padding="5")
        login_frame.pack(fill=tk.X, pady=5)

        ttk.Label(login_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.username_var, width=40).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password_var, width=40, show="*").grid(row=1, column=1, padx=5, pady=2)

        # ========== 购票设置 ==========
        settings_frame = ttk.LabelFrame(main_frame, text="购票设置", padding="5")
        settings_frame.pack(fill=tk.X, pady=5)

        # 支付方式
        ttk.Label(settings_frame, text="支付方式:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.payment_var = tk.StringVar(value="CONVENIENCE")
        payment_combo = ttk.Combobox(settings_frame, textvariable=self.payment_var, width=20, state="readonly")
        payment_combo['values'] = ("CONVENIENCE", "CREDIT_CARD", "NET_BANKING")
        payment_combo.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        # 票数策略
        ttk.Label(settings_frame, text="票数策略:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.strategy_var = tk.StringVar(value="MAX")
        strategy_combo = ttk.Combobox(settings_frame, textvariable=self.strategy_var, width=20, state="readonly")
        strategy_combo['values'] = ("MAX", "MIN", "SPECIFIC")
        strategy_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        # 指定票数
        ttk.Label(settings_frame, text="指定票数:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.quantity_var = tk.StringVar(value="2")
        ttk.Spinbox(settings_frame, textvariable=self.quantity_var, from_=1, to=10, width=5).grid(row=1, column=3, padx=5, pady=2)

        # 自动确认购买
        self.auto_confirm_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="自动确认购买（危险！）", variable=self.auto_confirm_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # ========== 控制按钮 ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="开始抢票", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="加载配置", command=self.load_config).pack(side=tk.RIGHT, padx=5)

        # ========== 日志区域 ==========
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 加载配置
        self.load_config()

    def log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_config(self):
        """保存配置到.env文件"""
        config_path = APP_DIR / ".env"
        content = f"""# eplus.jp 自动购票配置
TICKET_URL={self.url_var.get()}
EPLUS_USERNAME={self.username_var.get()}
EPLUS_PASSWORD={self.password_var.get()}
PAYMENT_METHOD={self.payment_var.get()}
TICKET_QUANTITY_STRATEGY={self.strategy_var.get()}
TICKET_QUANTITY={self.quantity_var.get()}
AUTO_CONFIRM_PURCHASE={'true' if self.auto_confirm_var.get() else 'false'}
CHROME_PATH={CHROME_PATH}
WAIT_TIMEOUT=10
ACTION_DELAY=0.1
"""
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.log("[INFO] 配置已保存")

    def load_config(self):
        """从.env文件加载配置"""
        config_path = APP_DIR / ".env"
        if not config_path.exists():
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'TICKET_URL':
                            self.url_var.set(value)
                        elif key == 'EPLUS_USERNAME':
                            self.username_var.set(value)
                        elif key == 'EPLUS_PASSWORD':
                            self.password_var.set(value)
                        elif key == 'PAYMENT_METHOD':
                            self.payment_var.set(value)
                        elif key == 'TICKET_QUANTITY_STRATEGY':
                            self.strategy_var.set(value)
                        elif key == 'TICKET_QUANTITY':
                            self.quantity_var.set(value)
                        elif key == 'AUTO_CONFIRM_PURCHASE':
                            self.auto_confirm_var.set(value.lower() == 'true')
            self.log("[INFO] 配置已加载")
        except Exception as e:
            self.log(f"[WARN] 加载配置失败: {e}")

    def start_automation(self):
        """开始自动化"""
        if not self.url_var.get():
            messagebox.showerror("错误", "请输入票务URL")
            return
        if not self.username_var.get() or not self.password_var.get():
            messagebox.showerror("错误", "请输入用户名和密码")
            return

        self.save_config()
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # 在新线程中运行
        thread = threading.Thread(target=self.run_automation, daemon=True)
        thread.start()

    def stop_automation(self):
        """停止自动化"""
        self.running = False
        self.log("[INFO] 正在停止...")
        if self.automation and self.automation.driver:
            try:
                self.automation.driver.quit()
            except:
                pass
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def run_automation(self):
        """运行自动化（在新线程中）"""
        try:
            # 导入自动化模块
            from eplus_auto import EplusConfig, EplusAutomation

            # 创建配置
            config = EplusConfig(
                ticket_url=self.url_var.get(),
                username=self.username_var.get(),
                password=self.password_var.get(),
                chrome_path=str(CHROME_PATH),
                payment_method=self.get_payment_method(),
                ticket_quantity_strategy=self.get_quantity_strategy(),
                ticket_quantity=int(self.quantity_var.get()),
                auto_confirm_purchase=self.auto_confirm_var.get()
            )

            # 重定向print到日志
            self.automation = EplusAutomation(config)
            self.automation.log_callback = lambda msg: self.root.after(0, self.log, msg)

            self.log("[INFO] 开始运行...")
            self.automation.run()

        except Exception as e:
            self.root.after(0, self.log, f"[ERROR] {e}")
        finally:
            self.root.after(0, self.on_automation_done)

    def on_automation_done(self):
        """自动化完成"""
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def get_payment_method(self):
        """获取支付方式枚举"""
        from eplus_auto import PaymentMethod
        mapping = {
            'CREDIT_CARD': PaymentMethod.CREDIT_CARD,
            'CONVENIENCE': PaymentMethod.CONVENIENCE,
            'NET_BANKING': PaymentMethod.NET_BANKING
        }
        return mapping.get(self.payment_var.get(), PaymentMethod.CONVENIENCE)

    def get_quantity_strategy(self):
        """获取票数策略枚举"""
        from eplus_auto import TicketQuantityStrategy
        mapping = {
            'MAX': TicketQuantityStrategy.MAX,
            'MIN': TicketQuantityStrategy.MIN,
            'SPECIFIC': TicketQuantityStrategy.SPECIFIC
        }
        return mapping.get(self.strategy_var.get(), TicketQuantityStrategy.MAX)

    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    app = EplusGUI()
    app.run()


if __name__ == '__main__':
    main()
