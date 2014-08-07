# -*- coding: utf-8 -*-

from app import app
from database import db
from models import User
from flask_peewee.auth import Auth

auth = Auth(app, db, user_model=User, prefix='')
