# -*- coding: utf-8 -*-

from peewee import *

DATABASE = 'runbot.db'
database = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = database   
                
class Project(BaseModel):
    name = CharField()
    version = CharField()
    db_path = CharField(null=True)
    modules = TextField(null=True)
    server = CharField()
    openerp_web = CharField(null=True)
    web_client = CharField(null=True)
    to_test = ForeignKeyField('self', null=True, related_name='test_branches')

class Addon(BaseModel):
    number = IntegerField()
    repo = CharField()
    project = ForeignKeyField(Project, related_name='addons')
    brancheable = BooleanField()
    custom = BooleanField()

    class Meta:
        ordering = ('number')
    
class Download(BaseModel):
    project = ForeignKeyField(Project, related_name='downloads')
    path = CharField(null=True)
    file_path = CharField(null=True)
    command = CharField()
    
def create_tables():
    print "Creando TABLAAAAAAAAAAAAAAAAAAAS"
    database.connect()
    if not Project.table_exists():
        Project.create_table()
    if not Addon.table_exists():
        Addon.create_table()
    if not Download.table_exists():
        Download.create_table()
    
