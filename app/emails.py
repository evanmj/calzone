from flask import render_template
from flask.ext.mail import Message
from app import mail
from decorators import async
from app import models

@async
def send_async_email(msg):
    mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)

    
def alarm_notification(ZoneName):

    #pull users from DB (TODO: This is untested)
    MainAdmin = models.User.query.filter_by(role = '1').first()
    EmailUsers = models.Email.query.all()

    send_email("[piSecurity] Zone: " + ZoneName + " Breach!  Alarm will sound shortly.",
        MainAdmin.email, #sender
        EmailUsers, #recipeients
        render_template("alarm_email.txt", 
            ZoneName = ZoneName),
        render_template("alarm_email.html",
            ZoneName = ZoneName))

