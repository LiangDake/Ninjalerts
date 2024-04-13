
import time
from utils_common.MetaMaskUtils import MetaMaskUtils
from utils_common.UC_ChomeUtils import UC_ChomeUtils
from utils_common.IpUtils import get_public_ip
from utils_common.NumberUtils import *
from utils_common.WalletUtils import *
from database.DataUtils import DataUtils
from database.SqlUtils import SqlUtils
import utils_common.Constants as Constants
import socket
import json
from selenium.webdriver.common.by import By
import os
import datetime
import pyperclip
import pyautogui
from utils_common.BrowserUtils import open_browser
import pyperclip
from selenium.webdriver.common.keys import Keys

import imaplib
import email
from email.header import decode_header
from lxml import html
PASSWORD = Constants.PASSWORD


class Main_Class():

    def __init__(self):
        self.datautils = DataUtils()
        self.sql_utils = SqlUtils()


    def get_email_text(self, username, mail_xpath):
        a = None
        server = ''
        password = ''
        sender_text = '.'
        # 连接到邮箱服务器
        imap = imaplib.IMAP4(server)
        imap.login(username, password)
        imap.select('INBOX')  # 选择收件箱

        # 搜索最新的 10 封邮件
        status, messages = imap.search(None, 'ALL')
        messages = messages[0].split(b' ')
        messages = messages[-1:]  # 取最新的 1 封邮件

        # 遍历每封邮件
        for mail_id in messages:
            _, msg = imap.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg[0][1])

            # 获取邮件主题和发件人
            subject = decode_header(msg['Subject'])[0][0]
            if isinstance(subject, bytes):
                # 如果主题是 bytes 类型，则解码为 str 类型
                subject = subject.decode()
            sender = decode_header(msg['From'])[0][0]
            if isinstance(sender, bytes):
                # 如果发件人是 bytes 类型，则解码为 str 类型
                sender = sender.decode()

            # 如果发件人包含指定字符串，则读取邮件内容
            if sender_text in sender:

                # 解析 HTML 内容，并查找指定的链接
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/html':
                            content = part.get_payload(decode=True).decode()
                            tree = html.fromstring(content)
                            elements = tree.xpath(mail_xpath)
                            if elements:
                                a = elements[0].text_content()

                else:
                    if msg.get_content_type() == 'text/html':
                        content = msg.get_payload(decode=True).decode()
                        tree = html.fromstring(content)
                        # elements = tree.xpath('//*[contains(@style, "font-family: HarmonyOS_Sans_Regular")]')
                        elements = tree.xpath(mail_xpath)
                        if elements:
                            a = elements[0].text_content()

        imap.close()
        imap.logout()
        return a

    def runBusiness(self, item):
        finger = item['finger']
        config = json.loads(item['config'])
        if 'finger' in str(config):
            finger = config['finger']
        self.metamask = open_browser(finger, sn_task=item['snTask'])
        if not self.metamask.driver:
            print('config配置浏览器错误')
            remark = 'config配置浏览器错误'
            return Constants.FAILED, remark

        try:
            self.metamask.unlock_metamask()
            # 解锁Xverse Wallet
            self.metamask.driver.get("chrome-extension://idnnbdplmphpflfnlkomgpfbpcgelopg/popup.html")
            pwd_input_element = self.metamask.xpath('//*[@id="app"]/div[1]/div/div/div[2]/input')
            pwd_input_element.send_keys(Keys.CONTROL, 'a')
            pwd_input_element.send_keys("Nxhlwxd6666")
            element = self.metamask.xpath("//*[contains(text(),'Unlock')]")
            element.click()
            while True:
                try:
                    element = self.metamask.xpath("//*[contains(text(),'total balance')]")
                    if element:
                        break
                except Exception as e:
                    print('等待解锁Xverse Wallet')
            url_sn = 313
            tencent_list = self.datautils.get_task_tencent_content_by_finger(url_sn, finger)
            if len(tencent_list) == 0:
                return Constants.FAILED, "邀请链接不存在"
            web_url = tencent_list[0]['content']
            print(f"当前邀请链接：{web_url}")
            self.metamask.driver.get(web_url)
            time.sleep(20)
            print("点击Create An Account")
            element = self.metamask.xpath("//*[contains(text(),'Create An Account')]")
            if element:
                try:
                    element.click()
                    sn = 225
                    tencent_list = self.datautils.get_task_tencent_content_by_finger(sn, finger)
                    if len(tencent_list) == 0:
                        return Constants.FAILED, "邮箱不存在"
                    mail = tencent_list[0]['content']
                    print(f"开始输入邮箱：{mail}")
                    input_element = self.metamask.xpath('//*[@id="onboarding_emailAddress"]')
                    input_element.send_keys(Keys.CONTROL, 'a')
                    input_element.send_keys(mail)
                    time.sleep(2)
                    print('点击Continue')
                    element = self.metamask.xpath("//*[contains(@id,'onboarding_continue') and contains(text(),'Continue')]")
                    if element:
                        element.click()
                    # 读取邮箱
                    mail_xpath = "//strong[contains(@style, 'font-weight: 600')]"
                    while True:
                        try:
                            email_code = self.get_email_text(mail, mail_xpath)
                            print(f'当前验证码：{email_code}')
                            if len(email_code) > 0:
                                break
                        except Exception as e:
                            print(f'获取验证码失败：{e}')
                    # 填入邮箱， 不需要点击Continue
                    input_element = self.metamask.xpath('//*[@id="otp1"]')
                    input_element.send_keys(Keys.CONTROL, 'a')
                    input_element.send_keys(email_code)
                    while True:
                        try:
                            elements = self.metamask.driver.find_elements(By.XPATH, "//*[contains(text(),'Add Alert')]")
                            if len(elements) < 3:
                                continue
                            elements[0].click()
                            elements[1].click()
                            elements[2].click()
                            break
                        except Exception as e:
                            pass
                    print('关注3个钱包完成，点击continue')
                    element = self.metamask.xpath("//*[contains(@id,'onboarding_continue') and contains(text(),'Continue')]")
                    if element:
                        element.click()
                    print('不需要提醒，点击continue——1')
                    element = self.metamask.xpath("//*[contains(@id,'onboarding_continue') and contains(text(),'Continue')]")
                    if element:
                        element.click()
                    print('不需要提醒，点击continue——2')
                    element = self.metamask.xpath("//*[contains(@id,'onboarding_continue') and contains(text(),'Continue')]")
                    if element:
                        element.click()
                except Exception as e:
                    print('邮箱步骤已填写完成')
            print('开始Connect XVerse Wallet')
            while True:
                try:
                    element = self.metamask.xpath("//*[contains(text(),'Connect XVerse Wallet')]")
                    if element:
                        element.click()
                        signin_window_handle = None
                        main_window_handle = self.metamask.driver.current_window_handle

                        while not signin_window_handle:
                            for handle in self.metamask.driver.window_handles:
                                if handle != main_window_handle:
                                    signin_window_handle = handle

                            time.sleep(1)
                        self.metamask.driver.switch_to.window(signin_window_handle)
                        element = self.metamask.xpath("//*[contains(text(),'Approve')]")
                        if element:
                            element.click()
                        self.metamask.driver.switch_to.window(main_window_handle)
                        print('等待确认窗口')
                        while True:
                            try:
                                element = self.metamask.xpath(
                                    "//*[contains(@id,'alert_confirm') and contains(text(),'OK')]")
                                if element:
                                    element.click()
                                    break
                            except Exception as e:
                                pass
                        break
                except Exception as e:
                    print('Connect XVerse Wallet连接步骤已填写完成')
                    break

            print('开始连接推特')
            element = self.metamask.xpath("//*[contains(text(),'Connect Your Twitter Account')]")
            if element:
                try:
                    element.click()
                    signin_window_handle = None
                    main_window_handle = self.metamask.driver.current_window_handle

                    while not signin_window_handle:
                        for handle in self.metamask.driver.window_handles:
                            if handle != main_window_handle:
                                signin_window_handle = handle

                        time.sleep(1)
                    self.metamask.driver.switch_to.window(signin_window_handle)
                    element = self.metamask.xpath('//*[@id="allow"]')
                    if element is None:
                        return Constants.FAILED, "推特不存在，退出"
                    element.click()
                    self.metamask.driver.switch_to.window(main_window_handle)
                except Exception as e:
                    print('推特已完成连接')
            time.sleep(20)
            if len(self.metamask.driver.window_handles) > 1:
                return Constants.FAILED, "推特授权失败，推特有问题，退出"
            print('开始连接小狐狸')
            while True:
                try:
                    element = self.metamask.xpath("//*[contains(text(),'Connect Your Metamask Wallet')]")
                    if element:
                        element.click()
                        break
                except Exception as e:
                    pass
            self.metamask.metamask_connect()
            element = self.metamask.xpath("//*[contains(text(),'Connect Your Metamask Wallet')]")
            if element:
                element.click()
            self.metamask.metamask_sign_new()
            time.sleep(5)
            return Constants.SUCCESS, "ninjalerts创建账号成功"
        except Exception as e:
            print(e)
            message = "系统异常，请检查"
            return Constants.FAILED, message
