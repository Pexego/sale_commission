# -*- coding: utf-8 -*-

from flask import Flask, render_template, send_file, redirect
import ConfigParser
from app import app
import os
import sys
from auth import auth
    
@app.route('/')
@auth.login_required
def index():
    return render_template("index.html")

@app.route('/project/<project_name>')
def project_detail(project_name):
    return render_template(project_name + ".html")
    
@app.route('/static/<path>')
def catch_all(r, path):
    return send_file("../static/" + path)
    
@app.route('/openerp/<job_id>')
def open_instance(job_id):
    urls_file = ConfigParser.ConfigParser()
    urls_file.read(os.path.join(os.path.dirname(sys.modules['__main__'].__file__),'urls.conf'))
    return redirect(urls_file.get("instances",str(job_id)))
