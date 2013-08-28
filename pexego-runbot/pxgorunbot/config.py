# -*- coding: utf-8 -*-

class Config(object):
    SECRET_KEY = 'A0Zr18h/3yX R~XHH!jmN]LWX/,?RT'
    DATABASE = {'engine': 'peewee.SqliteDatabase',
                'name': 'runbot.db'}
    SEND_FILE_MAX_AGE_DEFAULT = 60
    
    MY_DOMAIN = "runbot.pexego.es"
