import imaplib
import email
from lxml import html


def get_email_text(username, password, element_xpath): # 输入用户名、密码以及元素路径
    a = None
    server = "outlook.office365.com"
    # 连接到邮箱服务器
    imap = imaplib.IMAP4_SSL(server)
    imap.login(username, password)
    imap.select('INBOX')  # 选择收件箱

    # 获取到表示邮箱数量的List，内容为[b'1 2 3'], [b'1 2 3'], [b'1 2 3']...
    status, messages_num = imap.search(None, 'ALL')
    # 其中，messages_num[0]表示第一个列表里面的内容
    messages_num = messages_num[0].split() # message_num[0]，即为 b'1 2 3'

    # 获取邮件数量的数组，取最新的 1 封邮件 [b'23']
    # 如果是 messages_num[-1]，只能得到 b'23'
    # 如果是 messages_num[-2:]，得到 [b'23'] 以及 [b'22']
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


# get_email_text('gulfxhr@outlook.com', 'nCDbIf&^Nl0z', "//strong[contains(@style, 'font-weight: 600')]")
get_email_text('korecialbia1@hotmail.com', "XpYs8016", '//strong[contains(@style, "font-weight: 600")]')