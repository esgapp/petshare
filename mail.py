from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

with open("config.json") as config_file:
    config = json.load(config_file)

EMAIL_HOST = config['EMAIL_HOST']
EMAIL_ADDRESS = config['EMAIL_ADDRESS']
EMAIL_PASSWORD = config['EMAIL_PASSWORD']

def sendEmail(email, title, contents):
    s = smtplib.SMTP(host=EMAIL_HOST)
    s.starttls()
    s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    msg = MIMEMultipart()
    message = contents
    msg['From']=EMAIL_ADDRESS
    msg['To']=email
    msg['Subject']=title
    msg.attach(MIMEText(message, 'plain'))
    s.send_message(msg)
    del msg
