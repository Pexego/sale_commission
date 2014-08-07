"""
The OpenERP Runbot library (i.e. code to support the openerp-runbot script).
"""
import Queue
import re

from . import config
from . import app
from . import database
from . import models
from . import auth
from . import admin
from . import core
from . import misc
from . import server
from . import views
from . import templates

# Regex to match a unique branch name, e.g. ~openerp/openobject-server/trunk.
branch_input_re = re.compile('~(.+)/(.+)/(.+)')

# State saved to/restored from the file static/state.runbot (in JSON).
state = {}

# Commands sent from some thread to the main thread.
queue = Queue.Queue()

