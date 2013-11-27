#!/usr/bin/python
import os, subprocess, sys
subprocess.call(['python', 'virtualenv.py', 'flask'])
if sys.platform == 'win32':
    bin = 'Scripts'
else:
    bin = 'bin'
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask==0.9'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-login==0.1.3'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-openid==1.1.1'])
if sys.platform == 'win32':
    subprocess.call([os.path.join('flask', bin, 'pip'), 'install', '--no-deps', 'lamson', 'chardet', 'flask-mail==0.8.2'])
else:
    subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-mail==0.8.2'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy==0.7.9'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-sqlalchemy==0.16'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy-migrate==0.7.2'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-whooshalchemy==0.55a'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-wtf==0.8.3'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-babel==0.8'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flup==1.0.3.dev-20110405'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'tinysmtp==0.1.2'])
