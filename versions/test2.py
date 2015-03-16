#!/usr/bin/python

import smtplib

sender = 'dmichelson@ashevillenc.gov'
receivers = ['dmichelson@ashevillenc.gov']

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

smtpObj = smtplib.SMTP('192.168.0.102')
smtpObj.sendmail(sender, receivers, message)         
