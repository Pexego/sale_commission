# -*- coding: utf-8 -*-

from flask import *
import os
import config

#
# Create and configure the application object.
#
cur_path = os.path.abspath('.')
dest = os.path.join(cur_path,'static')

app = Flask(__name__, template_folder=dest, static_folder=dest)
app.config.from_object(config.Config)
