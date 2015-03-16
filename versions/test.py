import smtplib
import logging,logging.handlers 
smtpHandler = logging.handlers.SMTPHandler(mailhost=("192.168.0.102",25), fromaddr="dmichelson@ashevillenc.gov", toaddrs="dmichelson@ashevillenc.gov", subject=u"error message") 

LOG = logging.getLogger() 
LOG.addHandler(smtpHandler) 

LOG.error(u"tes1") 
LOG.error(u"test2") 
