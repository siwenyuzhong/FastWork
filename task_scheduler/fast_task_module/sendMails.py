import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 发送邮箱服务器
smtpserver = 'smtp.163.com'

# 用户
username = USERNAME
# 密码
password = PASSWORD
# 发送主题
subject = SUBJECT
# 发送内容
content = CONTENT
# 收件人
receiver = RECEICER


def sendEmails():
    # 编写HTML类型的邮件正文
    msg = MIMEText('<html><h1>{}</h1></html>'.format(content), 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['from'] = username
    msg['to'] = receiver

    # 发送邮件
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(username, receiver, msg.as_string())
    smtp.quit()
    print("向 {} 发送邮件成功".format(receiver))


if __name__ == '__main__':
    sendEmails()
