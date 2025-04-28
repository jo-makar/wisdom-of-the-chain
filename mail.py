#!/usr/bin/env python3
# Email the contents of stdin, configured via mail.json

from email.mime.text import MIMEText
import json
import smtplib
import sys

with open('mail.json') as file:
    config = json.load(file)

body = sys.stdin.read()
msg = MIMEText(body)
msg['Subject'] = 'wisdom-of-the-chain: scraper-yahoo-finance logs'
msg['From'] = config['sender']
msg['To'] = config['recipient']

with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port']) as server:
    server.login(config['username'], config['password'])
    server.sendmail(config['sender'], config['recipient'], msg.as_string())
