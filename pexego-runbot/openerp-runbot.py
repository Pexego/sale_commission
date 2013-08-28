#!/usr/bin/env python
"""
OpenERP Runbot, startup script.
"""

import optparse
import os
import sys

import pxgorunbot
from flask import Flask

def runbot_init(wd):
    """Create the directoy structure necessary by the runbot."""
    dest = os.path.join(wd,'repo')
    if not os.path.exists(dest):
        pxgorunbot.core.run(["bzr","init-repo",dest])
    for i in ['static',]:
        dest = os.path.join(wd,i)
        if not os.path.exists(dest):
            os.mkdir(dest)
    path = os.path.dirname(sys.modules['__main__'].__file__)
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "css"), "static/css"])
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "font"), "static/font"])
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "img"), "static/img"])
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "js"), "static/js"])
    pxgorunbot.core.run(["cp", os.path.join(path, "favicon.ico"), "static/"])
    #pxgorunbot.core.run(["cp", os.path.join(path, "logo.png"), "static/img"])
    pxgorunbot.core.run(["cp", os.path.join(path, "robots.txt"), "static/"])
    pxgorunbot.core.run('sudo su - postgres -c "createuser -s $USER"')
    #pxgorunbot.core.run('sudo su - postgres -c "createuser -s runbot"')
    pxgorunbot.models.create_tables()

def runbot_clean(wd):
    """Remove the directory structure created by `runbot_init()`. Quite unsafe.
    """
    dest = os.path.join(wd,'repo')
    pxgorunbot.core.run(["rm","-rf",dest])
    for i in ['static',]:
        dest = os.path.join(wd,i)
        pxgorunbot.core.run(["rm","-rf",dest])

def runbot_kill_msg():
    print "You can kill all the processes spawned by the runbot with the"
    print "following command:"
    print "  kill ` ps faux | grep ./static  | awk '{print $2}' `"

def main():
    parser = optparse.OptionParser(usage="%prog [--init|--run|--clean] [options] ",version="1.0")
    parser.add_option("--init", action="store_true", help="initialize the runbot environment")
    parser.add_option("--run", action="store_true", help="run the runbot")
    parser.add_option("--clean", action="store_true", help="remove any runbot-generated files (use `rm -rf`)")
    parser.add_option("--dir", metavar="DIR", default=".", help="runbot working dir (%default)")
    parser.add_option("--flask-port", metavar="PORT", default=5000, help="starting port for flask server (%default)")
    parser.add_option("--number", metavar="NUMBER", default=16, help="max concurrent instance to run (%default)")
    parser.add_option("--test", metavar="INT", default=1, help="run tests flag (%default)")
    parser.add_option("--start-job-id", metavar="INT", default=0, help="initial job id (%default)")
    parser.add_option("--debug", action="store_true", default=0, help="ease debugging by e.g. limiting branches")
    
    o, a = parser.parse_args(sys.argv)
    if o.init:
        runbot_init(o.dir)
    elif o.clean:
        runbot_clean(o.dir)
    elif o.run:
        pxgorunbot.server.start_server(int(o.flask_port),o.dir)
        server_net_port = int(o.flask_port) + int(o.number) * 2
        server_xml_port = int(o.flask_port) + int(o.number) * 4
        client_web_port = int(o.flask_port) + int(o.number) * 6

        r = pxgorunbot.core.RunBot(o.dir, server_net_port,
            server_xml_port, client_web_port, o.number, o.flask_port, o.test, int(o.start_job_id),
            o.debug)
        runbot_kill_msg()
        r.loop()
        runbot_kill_msg()
        print "Last used job id:", r.current_job_id
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

