# -*- coding: utf-8 -*-

from flask_peewee.admin import Admin, ModelAdmin
from auth import auth
from app import app
from models import User, Project, Download, Addon

class UserAdmin(ModelAdmin):
    columns = ('username', 'email', 'admin',)
    
class ProjectAdmin(ModelAdmin):
    columns = ('name', 'version',)
    
class DownloadAdmin(ModelAdmin):
    columns = ('project', 'command',)
    foreign_key_lookups = {'project': 'name'}
    
class AddonAdmin(ModelAdmin):
    columns = ('project', 'number', 'repo', 'custom',)
    foreign_key_lookups = {'project': 'name'}

admin = Admin(app, auth)
auth.register_admin(admin)

admin.register(User, UserAdmin)
admin.register(Project, ProjectAdmin)
admin.register(Addon, AddonAdmin)
admin.register(Download, DownloadAdmin)
    
admin.setup()
