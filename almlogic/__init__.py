import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

almlogic = Flask(__name__)
almlogic.config.from_object('config')
db = SQLAlchemy(almlogic)
mail = Mail(almlogic)
