"""
Runbot dynamic web server, to handle stickiness changes, build command and
teams and branches registration.
"""
import os
import simplejson
import threading
import urllib
import urlparse
import pxgorunbot
from app import app
import sys

def serve(port, folder):
    app.run(host='0.0.0.0')
    app.run(port=port, extra_files=['../urls.conf'], )
    print 'HTTP service (Flask) running on port %s' % port


def start_server(port, folder):    
    threading.Thread(target=serve,args=(port,folder,)).start()
    
def stop_server():    
    sys.exit(1)
    

