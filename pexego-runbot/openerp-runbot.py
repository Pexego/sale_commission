#!/usr/bin/env python
"""
OpenERP Runbot, startup script.
"""

import optparse
import os
import sys

import pxgorunbot

def runbot_init(wd):
    """Create the directoy structure necessary by the runbot."""
    dest = os.path.join(wd,'repo')
    if not os.path.exists(dest):
        pxgorunbot.core.run(["bzr","init-repo",dest])
    for i in ['nginx','static','lpcache',]:
        dest = os.path.join(wd,i)
        if not os.path.exists(dest):
            os.mkdir(dest)
    path = os.path.dirname(sys.modules['__main__'].__file__)
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "css"), "static/"])
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "font"), "static/"])
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "img"), "static/"])
    pxgorunbot.core.run(["cp", "-r", os.path.join(path, "js"), "static/"])
    pxgorunbot.core.run(["cp", os.path.join(path, "favicon.ico"), "static/"])
    pxgorunbot.core.run(["cp", os.path.join(path, "style.css"), "static/"])
    pxgorunbot.core.run(["cp", os.path.join(path, "logo.png"), "static/"])
    pxgorunbot.core.run(["cp", os.path.join(path, "robots.txt"), "static/"])
    pxgorunbot.core.run('sudo su - postgres -c "createuser -s $USER"')

def runbot_clean(wd):
    """Remove the directory structure created by `runbot_init()`. Quite unsafe.
    """
    dest = os.path.join(wd,'repo')
    pxgorunbot.core.run(["rm","-rf",dest])
    for i in ['nginx','static','lpcache']:
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
    parser.add_option("--nginx-domain", metavar="DOMAIN", default="pxgorunbot", help="virtual host domain (%default)")
    parser.add_option("--nginx-port", metavar="PORT", default=9009, help="starting port for nginx server (%default)")
    parser.add_option("--number", metavar="NUMBER", default=16, help="max concurrent instance to run (%default)")
    parser.add_option("--test", metavar="INT", default=1, help="run tests flag (%default)")
    parser.add_option("--start-job-id", metavar="INT", default=0, help="initial job id (%default)")
    parser.add_option("--debug", action="store_true", help="ease debugging by e.g. limiting branches")
    parser.add_option("--config", action="store_true", metavar="DIR", default="./config/runbot.conf", help="runbot configuration file")
    o, a = parser.parse_args(sys.argv)
    if o.init:
        runbot_init(o.dir)
    elif o.clean:
        runbot_clean(o.dir)
    elif o.run:
        pxgorunbot.server.read_state()
        pxgorunbot.server.start_server(int(o.nginx_port)-1)
        server_net_port = int(o.nginx_port) + int(o.number) * 2
        server_xml_port = int(o.nginx_port) + int(o.number) * 4
        client_web_port = int(o.nginx_port) + int(o.number) * 6

        r = pxgorunbot.core.RunBot(o.dir, server_net_port,
            server_xml_port, client_web_port, o.number, o.nginx_port,
            o.nginx_domain, o.test, int(o.start_job_id),
            o.debug)#, o.config)
        runbot_kill_msg()
        r.loop()
        runbot_kill_msg()
        print "Last used job id:", r.current_job_id
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

