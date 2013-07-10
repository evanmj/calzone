#flask imports
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

#app stuff
from app import app, db, lm, oid, models, admin
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin.base import MenuLink, Admin, BaseView, expose

#import forms Flask.wtf
from forms import LoginForm

#import database models for FlaskAlchemy
from models import User, Zones, History, AlarmStatus, ValidUsers, Settings, Email
from models import ROLE_USER, ROLE_ADMIN

#import python exensions
from datetime import datetime
import re
import subprocess

#import pre-defined emails
from emails import alarm_notification

#Config zone history
#from config import NOTICES_PER_PAGE

#Get variables from config file
#from config import VALID_USERS, ADMINS

#globals
SystemArmed = False



def CheckProcessRunning(process):
    """This function checks that alarmlogic.py is running, since it builds the db and keeps information up to date."""
    s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
    for x in s.stdout:
        if re.search(process, x):
            return True
    return False
    

#User Loader Callback -
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

#any fuctions decorated with @before_request will run this first
@app.before_request
def before_request():
    g.user = current_user  #copy flask global into the g. global object

    #TODO: only check the proess if contnet is not static content... i e they want to go to a page that needs almlogic.
    #note: this might slow down the UI!  maybe just check on login page?  we would like to know if the process crashes though...
#    if CheckProcessRunning('alarmlogic.py') == False:
        #check request url to avoid redirect loop (rightmost 10 chars)
#        if request.path <> url_for('notrunning') and request.path[:7] <> '/static' and request.path[:8] <> '/favicon':
#            return redirect(url_for('notrunning'))
#    else:
        #user refreshed after starting app
#        if request.url[-10:] == url_for('notrunning')[-10:]:
#            return redirect(url_for('index'))


#handle 404 nicely
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

#handle 500 nicely
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

#default route
@app.route('/', methods = ['GET', 'POST'])

#index route
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    #get armed status from database.
    armed = AlarmStatus.query.filter_by(attribute = 'Armed').first()    
    if armed.value == '1':
	ArmedStatus = True
    else:
        ArmedStatus = False

    #notify user if a zone is not secured (but don't keep them from arming with that status)
    zonesbreached = Zones.query.filter_by(secured = 0).first()
    if zonesbreached is None:
        flash('All zones secured.') 
    else:
        flash('One or more zones not secured.') 
    
    return render_template('index.html',
        title = 'Overview', ArmedStatus = ArmedStatus)

#almlogic.py not running
@app.route('/notrunning')
def notrunning():
    #TODO: Allow user to (re)start almlogic.py if logged in?
    return render_template('notrunning.html',title = 'Doh. ')


#arm the system
@app.route('/arm')
@login_required
def arm():
    armed = AlarmStatus.query.filter_by(attribute = 'Armed').first()    
    armed.value = '1'
    db.session.add(armed)
    now = datetime.now()
    hist = History(source = g.user.nickname, event = 'Armed By User', timestamp = now)
    db.session.add(hist)
    db.session.commit()  #write data
    flash('The system has been Armed.')
    return redirect(url_for('index'))

#disarm the system
@app.route('/disarm')
@login_required
def disarm():
    #disarm the system (almlogic.py program handles that)
    armed = AlarmStatus.query.filter_by(attribute = 'Armed').first()
    armed.value = '0'
    db.session.add(armed)
    now = datetime.now()
    hist = History(source = g.user.nickname, event = 'Disarmed By User', timestamp = now)
    db.session.add(hist)
    db.session.commit()  #write data
    flash('The system has been Disarmed.')
    return redirect(url_for('index'))


#login route
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():  #do we have a valid logged in user?
        return redirect(url_for('index'))		#redirect to index
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data  #store remember me box of form to session variable
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])  #openID login call
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):

    #do we have valid users yet?
    user = User.query.filter_by(email = resp.email).first()  #find user in db
    if user is None:    #if not found... this is the first user to log in.  Make them admin for easy setup
        nickname = resp.nickname
        if nickname is None or nickname == "":  #build nickname if null
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_ADMIN)
        db.session.add(user)
        db.session.commit()
    # Is the email returned from OpenID valid, and is the user allowed on the system? 
    # query for this user
    Valid_Users = ValidUsers.query.filter_by(email = resp.email).first()
    #do we have any valid users yet?
    if Valid_Users is None:
        #no valid users, this is the admin logging in the first time.
        u = ValidUsers(email = resp.email)
        db.session.add(u)
        db.session.commit()
    #some valid users exist, do we have this user in our db?
    elif resp.email is None or resp.email == "" or resp.email not in Valid_Users.email:  
        flash('Invalid login. You have not been granted access to this system.')
        return redirect(url_for('login'))

    remember_me = False
    if 'remember_me' in session:  #do we want to remember this user?
        remember_me = session['remember_me']  #copy value from session
        session.pop('remember_me', None)      #clear session value..?
    login_user(user, remember = remember_me)  #feed flask the user and remember status
    return redirect(request.args.get('next') or url_for('index'))  #return page the user wanted, or index if none reqd.

#define log out user route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    

#define history route
@app.route('/history')
@app.route('/history/<int:page>')
@login_required
def history(page = 1):
    #pull paginated history from db... paginate(page,items per page,empty list on error)
    NumNotices = models.Settings.query.filter_by(attribute = 'NoticesPerPage').first()
    HISTORY = models.History.query.order_by("timestamp desc").paginate(page, int(NumNotices.value), False)
    return render_template('history.html',title = 'History', history = HISTORY,curr_page = page)  #pass history to history template
  
@app.route('/clearhistory')
@login_required
def clearhistory():
    #TODO: There is a better way to do this I'm sure.
    #TODO: Add Confirmation popup or something.  Also, this should go on the admin page.
    REMHIST = models.History.query.all()  #pull history data from database
    for delhist in REMHIST:
        db.session.delete(delhist)
    db.session.commit()
    flash('History Cleared by User.')
    return redirect(url_for('history'))
    

#define zones route
@app.route('/zones')
@login_required
def zones():
    ZONES = models.Zones.query.all()   #pull zones list from DB
    return render_template('zones.html',title = 'Zones',zones = ZONES) #pass ZONE information to zones template

#===================
#flask-Admin Section
#===================

#define custom flask-Admin view
class UserView(ModelView):
    # Disable model creation
    can_create = False
    can_edit = True
    can_delete = True

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(User, session, **kwargs)

    def is_accessible(self):
        if g.user.is_authenticated():
            return g.user.role #ROLE_ADMIN == 1, user = 0
        else:  #anonymous user
            return 0

class ZoneView(ModelView):

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(ZoneView, self).__init__(Zones, session, **kwargs)

    def is_accessible(self):
        if g.user.is_authenticated():
            return g.user.role #ROLE_ADMIN == 1, user = 0
        else:  #anonymous user
            return 0

class ValidUsersView(ModelView):

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(ValidUsersView, self).__init__(ValidUsers, session, **kwargs)

    def is_accessible(self):
        if g.user.is_authenticated():
            return g.user.role #ROLE_ADMIN == 1, user = 0
        else:  #anonymous user
            return 0

class SettingsView(ModelView):

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(SettingsView, self).__init__(Settings, session, **kwargs)

    def is_accessible(self):
        if g.user.is_authenticated():
            return g.user.role #ROLE_ADMIN == 1, user = 0
        else:  #anonymous user
            return 0

class EmailView(ModelView):

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(EmailView, self).__init__(Email, session, **kwargs)

    def is_accessible(self):
        if g.user.is_authenticated():
            return g.user.role #ROLE_ADMIN == 1, user = 0
        else:  #anonymous user
            return 0

#add flask admin views
admin.add_view(UserView(db.session))
admin.add_view(ZoneView(db.session))
admin.add_view(ValidUsersView(db.session))
admin.add_view(SettingsView(db.session))
admin.add_view(EmailView(db.session))
admin.add_link(MenuLink(name='Clear History', url='/clearhistory'))
admin.add_link(MenuLink(name='Exit Admin', url='/'))
