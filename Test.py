import csv
import imaplib
import email
from lxml import html
from telnetlib import EC

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from bit_api import *


# 网页元素基本操作
def element_input(path, content):  # 填入您需要操作的元素的路径以及内容
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, path))).send_keys(content)


def element_click(path):  # 填入您需要操作的元素的路径
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, path))).click()


def is_element_displayed(path):
    attempt = 5
    result = False
    while attempt > 0:
        try:
            driver.find_element(By.XPATH, path)
        except Exception:
            attempt -= 1
            time.sleep(1)
        else:
            result = True
            break
    return result


def web_jump_new():
    attempt = 5
    new_window_handle = None
    former_web = driver.current_window_handle
    while not new_window_handle and attempt > 0:
        for handle in driver.window_handles:
            if handle != former_web:
                new_window_handle = handle
        attempt -= 1
        time.sleep(1)
    driver.switch_to.window(new_window_handle)
    print(driver.title)
    return former_web


# 跳转至下一页面
def web_jump_next():
    handles = driver.window_handles
    driver.switch_to.window(handles[-1])


# 跳转至指定页面
def web_jump_to(handle):
    driver.switch_to.window(handle)


# 获取邮箱验证码
def get_email_text(username, password, element_xpath):  # 输入用户名、密码以及所需验证码的元素路径
    a = None
    server = "outlook.office365.com"
    # server = "imap.rambler.ru"
    # server = "imap.163.com"
    # 连接到邮箱服务器
    imap = imaplib.IMAP4_SSL(server)
    imap.login(username, password)
    time.sleep(5)
    imap.select('INBOX')  # 选择收件箱

    # 获取到表示邮箱数量的List，内容为[b'1 2 3'], [b'1 2 3'], [b'1 2 3']...
    status, messages_num = imap.search(None, 'ALL')
    # 其中，messages_num[0]表示第一个列表里面的内容
    messages_num = messages_num[0].split()  # message_num[0]，即为 b'1 2 3'

    # 获取邮件数量的数组，取最新的 1 封邮件 [b'23']
    # 如果是 messages_num[-1]，只能得到 b'23'
    # 如果是 messages_num[-2:]，得到最新的 2 封邮件
    messages_num = messages_num[-1:]

    # 遍历每封邮件
    for messages_num in messages_num:
        _, msg = imap.fetch(messages_num, "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        # 解析每一封邮件的 HTML 内容，并查找指定的链接
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                content = part.get_payload(decode=True).decode()
                tree = html.fromstring(content)
                elements = tree.xpath(element_xpath)
                a = elements[0].text_content()
                print(f"获取到最新邮件的验证码: {a}")
    imap.close()
    return a


def click_alert():
    # 关注前三个用户
    element_click('//*[@id="modalContainer"]/div[3]/div[3]/div/div[3]/div/div[3]/div[1]/div[2]/div')
    element_click('//*[@id="modalContainer"]/div[3]/div[3]/div/div[3]/div/div[3]/div[2]/div[2]/div')
    element_click('//*[@id="modalContainer"]/div[3]/div[3]/div/div[3]/div/div[3]/div[3]/div[2]/div')
    # Continue
    element_click('//*[@id="onboarding_continue"]')
    # Continue-1
    element_click('//*[@id="onboarding_continue"]')
    # Continue-2
    element_click('//*[@id="onboarding_continue"]')


# 导入账号信息
def account_import(csv_file_name, account_list):
    # 读取文件信息
    with open(csv_file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # 遍历CSV文件的每一行并添加到列表
        for row in csv_reader:
            # 以每一列为基础，分别为用户名，账号
            email_username, email_password, twitter_username, twitter_password = row
            # 循环遍历每一列的账号信息，即为新的导入账号信息
            new_account = {
                'Email_Username': email_username, 'Email_Password': email_password,
                'Twitter_Username': twitter_username, 'Twitter_Password': twitter_password
            }
            # 将每一列新的账号信息都导入至账号数组里
            account_list.append(new_account)
    print(f'{csv_file_name}导入成功！')
    print()


def account_upload(csv_file_name, account_list):
    with open(csv_file_name, 'a', newline='') as f:
        # Create a dictionary writer with the dict keys as column fieldnames
        writer = csv.DictWriter(f, fieldnames=account_list.keys())
        # Append single row to CSV
        writer.writerow(account_list)


# 推特登录
def twitter_login(twitter_username, twitter_password):
    driver.get('https://twitter.com/')
    time.sleep(3)
    # 若账号已登录
    if is_element_displayed('//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[2]/div/div/div/div/div['
                            '2]/div/div[2]/div/div/div[4]/div'):
        element_click('//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[2]/div/div/div/div/div[2]/div/div['
                      '2]/div/div/div[4]/div')
        # Log out
        element_click('//*[@id="layers"]/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/div/a[2]')
        # Twitter Log Out Confirm
        # Log out
        element_click('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]')
        # Log in
        element_click('/html/body/div/div/div/div[2]/main/div/div/div[1]/div/div/div[3]/div[5]/a')
    else:
        # Log in
        element_click('/html/body/div/div/div/div[2]/main/div/div/div[1]/div/div/div[3]/div[5]/a')
    # 输入账号
    web_jump_next()
    is_element_displayed('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div['
                         '2]/div/div/div/div[5]/label/div/div[2]/div/input')
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div['
                                  '2]/div/div/div/div[5]/label/div/div[2]/div/input').clear()
    element_input('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div['
                  '5]/label/div/div[2]/div/input', twitter_username)
    # 下一步
    is_element_displayed('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div['
                         '2]/div/div/div/div[6]')
    element_click('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div['
                  '2]/div/div/div/div[6]')
    # 输入密码
    is_element_displayed('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div['
                         '1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    element_input('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div['
                  '1]/div/div/div[3]/div/label/div/div[2]/div[1]/input', twitter_password)
    # 登录
    element_click('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div['
                  '2]/div/div[1]/div/div/div')
    time.sleep(5)
    print(f'推特账号 {twitter_username} 已登录成功')
    print()
    return True


# 邮箱注册新账号
def new_account_signup(email_username, email_password):
    # 点击Create An Account
    element_click('/html/body/div/div[1]/div[3]/div[2]/div[2]/div[2]/div[1]')
    # 输入邮箱
    if is_element_displayed('//*[@id="onboarding_emailAddress"]'):
        element_input('//*[@id="onboarding_emailAddress"]', email_username)
    # Continue
    element_click('//*[@id="onboarding_continue"]')
    # 等待获取邮箱验证码
    while True:
        try:
            verify_code = get_email_text(email_username, email_password,
                                         '//strong[contains(@style, "font-weight: 600")]')
            if len(verify_code) > 0:
                break  # 收到验证码后跳出循环，否则继续尝试获取
        except Exception as e:
            print(f'获取验证码失败：{e}')
            print()
            return False
    # 输入获得的验证码
    element_input('//*[@id="otp1"]', verify_code)
    # 若邮箱未注册
    if is_element_displayed('//*[@id="modalContainer"]/div[3]/div[3]/div/div[3]/div/div[3]/div[1]/div[2]/div'):
        # 成功后自动跳转关注页面
        # 关注前三个用户
        click_alert()
        while True:
            try:
                element_click('//*[@id="react-target"]/div[4]/div[1]')
                break
            except Exception as e:
                driver.refresh()
                click_alert()
        # 进入主页面
        print('邮箱注册步骤已完成')
        print("已成功进入主页面，即将开始链接Xverse钱包...")
        print()
        return True
    # 若邮箱已注册
    else:
        account_logout()
        return False


# 链接Xverse钱包
def xverse_wallet_connect(password):
    print('开始Connect XVerse Wallet')
    element_click('//*[@id="col2"]/div[2]/div[1]')
    # 跳转至钱包页面
    former_web = web_jump_new()
    # 钱包密码未输入时，先输入password
    if is_element_displayed('//*[@id="app"]/div[1]/div/div/div[2]/input'):
        element_input('//*[@id="app"]/div[1]/div/div/div[2]/input', password)
        # Unlock
        element_click('//*[@id="app"]/div[1]/div/div/div[3]/button')
    # 钱包密码已输入时，直接点击Approve
    element_click('//*[@id="app"]/div[1]/div[2]/div[2]/button')
    # 返回主页面
    web_jump_to(former_web)
    time.sleep(3)
    while True:
        if is_element_displayed('//*[@id="alert_confirm"]'):
            # 点击OK按钮
            element_click('//*[@id="alert_confirm"]')
            print('钱包链接成功！')
            print()
            time.sleep(1)
            break
    return True


# 链接Twitter账号
def twitter_connect():
    # 链接twitter
    element_click('//*[@id="col2"]/div[3]/div[1]')
    # 跳转至推特页面
    main_web = web_jump_new()
    while True:
        try:
            if is_element_displayed('//*[@id="allow"]'):
                # 授权登录
                element_click('//*[@id="allow"]')
                break
        except NoSuchElementException:
            print('此推特账号已注册!')
            print()
            return False
    # 跳转至主页面
    web_jump_to(main_web)
    # 账号注册成功
    print("推特链接成功！")
    print()
    time.sleep(1)
    return True


# 退出账号
def account_logout():
    # Account 按钮
    element_click('//*[@id="react-target"]/div[1]/div[2]/div/div[3]/div[1]/div[2]')
    time.sleep(1)
    # liangdake4@gmail.com
    element_click('//*[@id="react-target"]/div[1]/div[3]/div[1]/div[1]')
    # Sign Out 按钮
    element_click('//*[@id="currentModalContent"]/div[4]/div[2]/div[3]')
    time.sleep(3)
    # 账号已成功登出
    print("账号已成功登出！")
    print()
    return True


# 执行代码前确保邮箱账号密码正确
# 执行代码前确保主账号邀请链接正确
if __name__ == '__main__':
    # 初始化
    res = openBrowser('78d4da810d4649fc9762723e565a2118')  # 比特浏览器窗口ID
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", res['data']['http'])
    service = Service(executable_path=res['data']['driver'])
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # 创建账号列表
    account_list = []
    # 创建已注册账号列表
    signed_account_list = {'Email_Address': '', 'Email_Password': '', 'Twitter_Account': '', 'Twitter_Password': ''}
    # 记住每一个账号的顺序
    account_number = 0
    email_username = ''
    email_password = ''
    twitter_username = ''
    twitter_password = ''
    account_import('Accounts.csv', account_list)
    print(account_list)
    for email_accounts in account_list:
        email_username = email_accounts['Email_Username']
        email_password = email_accounts['Email_Password']
        twitter_username = email_accounts['Twitter_Username']
        twitter_password = email_accounts['Twitter_Password']
        print(twitter_username)

        # 进入推特页面登录账号
        # twitter_login(twitter_username, twitter_password)

        # 通过邀请链接进入页面
        # 确保点击的链接是主账号的邀请链接
        driver.get('https://www.ninjalerts.com/@liangdake')
        time.sleep(3)

        # 邮箱注册新账号成功:
        if new_account_signup('kat.simas@outlook.com', 'lIRRLlrN399'):
            # 链接Xverse钱包成功:
            if xverse_wallet_connect('Lkzxxzcsc2020'):
                # 链接推特账号成功:
                if twitter_connect():
                    # 账号注册成功，写入已注册账号列表
                    signed_account_list['Email_Address'] = email_username
                    signed_account_list['Email_Password'] = email_password
                    signed_account_list['Twitter_Account'] = twitter_username
                    signed_account_list['Twitter_Password'] = twitter_password
                    account_upload('Used_Accounts.csv', signed_account_list)
                    print("已注册账号信息已导入列表")
                    time.sleep(3)
                    account_logout()
                    # 退出账号，注册下一个账号
                    account_number += 1
                    print(f'账号{account_number}注册完成，邮箱号为{email_username}，推特号为{twitter_username}')
                    print()
                else:
                    account_number += 1
                    print(f'账号{account_number}注册失败，邮箱号为{email_username}')
                    continue
            else:
                account_number += 1
                print(f'账号{account_number}注册失败，邮箱号为{email_username}')
                continue
        else:
            account_number += 1
            print(f'账号{account_number}注册失败，邮箱号为{email_username}')
            continue
    print(f'{account_number}个账号已全部执行完毕，请检查未完成的账号')
