# -*- coding: utf-8 -*-

from flask_peewee.admin import Admin, ModelAdmin
from auth import auth
from app import app
from models import User, Project, Download, Addon

class UserAdmin(ModelAdmin):
    columns = ('username', 'email', 'admin',)
    
    def save_model(self, instance, form, adding=False):
        """
        @see https://github.com/coleifer/flask-peewee/blob/master/flask_peewee/auth.py#L58
        """
        orig_password = instance.password
        user = super(UserAdmin, self).save_model(instance, form, adding)
        if orig_password != form.password.data:
            user.set_password(form.password.data)
            user.save()
        return user
    
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
