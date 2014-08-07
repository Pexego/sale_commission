# -*- coding: utf-8 -*-

from peewee import *
from flask_peewee.auth import BaseUser
from database import db

class BaseModel(Model):
    class Meta:
        database = db   
        
class User(BaseModel, BaseUser):
    """
    User model.

    Note: follows the 'user model' protocol specified by flask_peewee.auth.Auth
    """
    username = CharField(max_length=30)
    password = CharField(max_length=46) # 5 bytes salt + '$' + 40 bytes SHA1 hex
    email = CharField(max_length=50)
    active = BooleanField(default=True)
    admin = BooleanField(default=False)

    def __unicode__(self):
        return self.username
                
class Project(BaseModel):
    name = CharField()
    version = CharField()
    db_path = CharField(null=True)
    modules = TextField(null=True)
    server = CharField()
    openerp_web = CharField(null=True)
    web_client = CharField(null=True)
    to_test = ForeignKeyField('self', null=True, related_name='test_branches')
    
    def __unicode__(self):
        return self.name

class Addon(BaseModel):
    number = IntegerField()
    repo = CharField()
    project = ForeignKeyField(Project, related_name='addons')
    brancheable = BooleanField()
    custom = BooleanField()

    class Meta:
        order_by = ('number',)
    
    def __unicode__(self):
        return self.repo
    
class Download(BaseModel):
    project = ForeignKeyField(Project, related_name='downloads')
    path = CharField(null=True)
    file_path = CharField(null=True)
    command = CharField()
    
    def __unicode__(self):
        return self.command
    
def create_tables():
    db.connect()
    if not User.table_exists():
        User.create_table()
        admin = User(username='admin', admin=True, active=True, email="omarcs7r@gmail.com")
        admin.set_password('admin')
        admin.save()
    if not Project.table_exists():
        Project.create_table()
    if not Addon.table_exists():
        Addon.create_table()
    if not Download.table_exists():
        Download.create_table()
    
create_tables()
