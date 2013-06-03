#flask imports
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

#app stuff
from app import app, db, lm, oid, models

#import forms Flask.wtf
from forms import LoginForm

#import database models for FlaskAlchemy
from models import User, History, AlarmStatus, ROLE_USER, ROLE_ADMIN

#import python exensions
from datetime import datetime

#import pre-defined emails
from emails import alarm_notification

#Config zone history
from config import NOTICES_PER_PAGE

#Get variables from config file
from config import VALID_USERS

#globals
SystemArmed = False

#User Loader Callback -
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

#any fuctions decorated with @before_request will run this first
@app.before_request
def before_request():
    g.user = current_user  #copy flask global into the g. global object

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
    armed = AlarmStatus.query.filter_by(attribute = 'Armed').first()    
    if armed.value == '1':
	ArmedStatus = True
    else:
        ArmedStatus = False
    flash('All Zones Okay') #TODO: add if statement for one or more zones not ready to arm
    return render_template('index.html',
        title = 'Overview', ArmedStatus = ArmedStatus)

#arm the system
@app.route('/arm')
def arm():
    #arm the system (almlogic.py program handles that)
    armed = AlarmStatus.query.filter_by(attribute = 'Armed').first()    
    armed.value = '1'
    db.session.add(armed)
    now = datetime.now()
    hist = History(source = g.user.nickname, event = 'Armed By User', timestamp = now)
    db.session.add(hist)
    db.session.commit()  #write data
    flash('The system has been Armed.')
#    alarm_notification('Test Zone')   #temp send alarm on arm
    return redirect(url_for('index'))

#disarm the system
@app.route('/disarm')
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
	# Is the email returned from OpenID valid, and is the user allowed on the system? (config.py)
    if resp.email is None or resp.email == "" or resp.email not in VALID_USERS:  
        flash('Invalid login. You have not been granted access to this system.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()  #find user in db
    if user is None:    #if not found... 
        nickname = resp.nickname
        if nickname is None or nickname == "":  #build nickname if null
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
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
    HISTORY = models.History.query.order_by("timestamp desc").paginate(page, NOTICES_PER_PAGE, False)
    return render_template('history.html',history = HISTORY,curr_page = page)  #pass history to history template
  
@app.route('/clearhistory')
@login_required
def clearhistory():
    #TODO: There is a better way to do this I'm sure.
    #TODO: Add Confirmation popup or something.  Also, this should go on the admin page.
    HISTORY = models.History.query.order_by("timestamp desc")  #pull history data from database
    for histdata in HISTORY:
        db.session.delete(histdata)
    db.session.commit()
    return render_template('history.html',history = HISTORY)  #pass history to history template
    

#define zones route
@app.route('/zones')
@login_required
def zones():
    ZONES = models.Zones.query.all()   #pull zones list from DB
    return render_template('zones.html',zones = ZONES) #pass ZONE information to zones template

