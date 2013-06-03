from hashlib import md5
from almlogic import alarmlogic
from almlogic import db
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
    value = db.Column(db.String(64), unique = True)

#settings table, written by web app, read by others... 
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    attribute = db.Column(db.String(64), unique = True)
    value = db.Column(db.String(64), unique = True)

#class UserList(db.Model):
#TODO: User list here for email list, txt list, etc.

class History(db.Model):
    id = db.Column(db.Integer, primary_key = True)      #pk
    source = db.Column(db.String(64))                   #source of entry... user, or zone that caused change
    event = db.Column(db.String(64))                    #type of event, arm, disarm, open, close, etc....
    timestamp = db.Column(db.DateTime)


#ideas for other tables...

# we will need an outputs table to trigger outputs.
# settings table should be populated initially with some obvious settings.  
# the goal would be to ditch user settings in config.py.
# once settings is populated, no need to re-populate, assume user has changed things. 
#
# a configurable database for email notices, with types mask... alarm notices, etc.
#
# config page will show for admins that allows changing of all the db settings, zones, pins, etc.
#
# also need a place for status, like global armed bit, and arm request bits, and whatnot.
# maybe for speed, an 'arm allowed' and 'arm inplace allowed' set of bits so flasks knows the answer already.
#
