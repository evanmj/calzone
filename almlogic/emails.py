#from flask import render_template
#from flask.ext.mail import Message
from tinysmtp import Connection, Message
from decorators import async
#from almlogic import almlogic #import this to get config vars
#almlogic.config.from_object('config')
#from almlogic import models

@async
def send_async_email(msg):
    #send email with tinysmtp  TODO: Use constants from config.py instead here.  This works for now.  Baby needs a bath.
    with Connection(hostname='smtp.googlemail.com',port=465, username='calzone.test', password='aeiouaeiou', ssl=False, tls=True) as conn:
        conn.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject = subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)

    
def alarm_notification(ZoneName):

    #pull users from DB (TODO: This is untested)
   # EmailUsers = models.Email.query.all()
   # MainAdmin = models.User.query.filter_by(role = '1').first()

    send_email(subject = "Zone: " + ZoneName + " Alarming Now!",
        sender = "Calzone", #sender
        recipients = ['evanmj@gmail.com'], #EmailUsers, #recipeients
        text_body = "Zone: " + ZoneName + " Alarming Now!",  # plain text users get this
        html_body = "Zone: " + ZoneName + " Alarming Now!")  # html users get this

#hack to make fake context requests to render templates
#def create_email(TemplateName,ArgName):
 #   with almlogic.test_request_context('/send_email'):
  #      return render_template(TemplateName, ZoneName=ArgName) 


