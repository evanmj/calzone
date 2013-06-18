from flask import render_template
from flask.ext.mail import Message
from app import mail
from decorators import async
from config import ADMINS
from config import VALID_USERS

@async
def send_async_email(msg):
    mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)

    
def alarm_notification(ZoneName):
    send_email("[piSecurity] Zone: " + ZoneName + " Breach!  Alarm will sound shortly.",
        ADMINS[0],
        VALID_USERS,
        render_template("alarm_email.txt", 
            ZoneName = ZoneName),
        render_template("alarm_email.html",
            ZoneName = ZoneName))

