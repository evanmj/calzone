from flask import render_template
from flask.ext.mail import Message
from almlogic import almlogic, mail
from decorators import async
#from almlogic import models

@async
def send_async_email(msg):
    with almlogic.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    with almlogic.app_context():
        #send_async_email(msg)
        mail.send(msg) #send synchronously

    
def alarm_notification(ZoneName):

    #pull users from DB (TODO: This is untested)
   # MainAdmin = models.User.query.filter_by(role = '1').first()
   # EmailUsers = models.Email.query.all()

    with almlogic.app_context():
        with almlogic.app_context():
            mail.init_app(almlogic)
            send_email("Zone: " + ZoneName + " Alarming Now!",
                '[Calzone]',#MainAdmin.email, #sender
                ['evanmj@gmail.com'], #EmailUsers, #recipeients
                create_email("alarm_email.txt",ZoneName),
                create_email("alarm_email.html",ZoneName))

#hack to make fake context requests to render templates
def create_email(TemplateName,ArgName):
    with almlogic.test_request_context('/send_email'):
        return render_template(TemplateName, ZoneName=ArgName) 
