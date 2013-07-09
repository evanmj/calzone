from hashlib import md5
from almlogic import db
import alarmlogic
from datetime import datetime

ROLE_USER = 0
ROLE_ADMIN = 1

#users, used for login handling
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

#zones, written by 'alarmlogic.py', read by flask.
class Zones(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    pin = db.Column(db.SmallInteger, unique = True)
    secured = db.Column(db.Boolean)

#status of the alarm system, written by 'alarmlogic.py'
class AlarmStatus(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    attribute = db.Column(db.String(64), unique = True)
    value = db.Column(db.String(64))

#settings table, written by web app, read by others... 
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    attribute = db.Column(db.String(64), unique = True)
    value = db.Column(db.String(64))
    description = db.Column(db.String(128))

class History(db.Model):
    id = db.Column(db.Integer, primary_key = True)      #pk
    source = db.Column(db.String(64))                   #source of entry... user, or zone that caused change
    event = db.Column(db.String(64))                    #type of event, arm, disarm, open, close, etc....
    timestamp = db.Column(db.DateTime)
