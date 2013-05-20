# -*- coding: utf-8 -*-


from app import app
from flask_peewee.db import Database

database = Database(app)
db = database.database
