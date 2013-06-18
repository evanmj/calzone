import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'make-this-something-that-nobody-would-ever-guess-5632344'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
    
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository') + '?check_same_thread=False'

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'

# administrator list
ADMINS = ['evanmj@gmail.com']

# users list
VALID_USERS = ['evanmj@gmail.com',
		'evan@squishybrained.com',]

# IO Update Interval
IOupdateRate = 0.5   #seconds

# zone defintion  #for now these populate the db until there is a web based input to change them
CONFIGZONES = [
     { 'name': 'Front Garage Door', 'pin': '0', 'secured': 0},
     { 'name': 'Back Door', 'pin': '1', 'secured': 0},
     { 'name': 'Living - Dining', 'pin': '2' , 'secured': 0 },
     { 'name': 'Kitchen - Family', 'pin': '3' , 'secured': 0 },
     { 'name': 'Game Room', 'pin': '4' , 'secured': 0 },
     { 'name': 'Front Bedroom 1', 'pin': '5' , 'secured': 0 },
     { 'name': 'Office', 'pin': '6' , 'secured': 0 },
     { 'name': 'Master Bedroom', 'pin': '7' , 'secured': 0 }]


# pagination
NOTICES_PER_PAGE = 15  # Number of notices per page of the zone history page

