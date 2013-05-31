import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

almlogic = Flask(__name__)
almlogic.config.from_object('config')
db = SQLAlchemy(almlogic)

from app import models

