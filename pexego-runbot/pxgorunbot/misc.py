"""
A few miscellaneous functions (logging, shell command calls, ...).
"""

import fcntl
import signal
import subprocess
import threading
import time
import os

__all__ = [
    'kill', 'log', 'run', 'run_output', 'run_and_get'
    ]

log_lock = threading.Lock()
def log(*l,**kw):
    out = []
    out.append(time.strftime("%Y-%m-%d %H:%M:%S"))
    t = threading.current_thread()
    if t.name.startswith('runbot-group-worker-'):
        out.append(t.name[13:])
    elif t.name == 'MainThread':
        out.append('main')
    else:
        out.append(t.name)
    for i in l:
        if not isinstance(i,basestring):
            i=repr(i)
        out.append(i)
    out+=["%s=%r"%(k,v) for k,v in kw.items()]
    print "LOG: ", out
    with log_lock:
        print " ".join(out)

def lock(name):
    fd=os.open(name,os.O_CREAT|os.O_RDWR,0600)
    fcntl.lockf(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)

def nowait():
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def run(l,env=None):
    log("run",l)
    env = dict(os.environ, **env) if env else None
    if isinstance(l,list):
        if env:
            rc = subprocess.call(l, env=env)
            #rc=os.spawnvpe(os.P_WAIT, l[0], l, env)
        else:
            rc=os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l,(str, unicode)):
        tmp=['sh','-c',l]
        if env:
            rc=os.spawnvpe(os.P_WAIT, tmp[0], tmp, env)
        else:
            rc=os.spawnvp(os.P_WAIT, tmp[0], tmp)
    return rc

def kill(pid,sig=9):
    try:
        os.kill(pid,sig)
    except OSError:
        pass

def run_output(l, cwd=None):
    return subprocess.Popen(l, cwd=cwd).communicate()[0]

def run_and_get(l, env=None):
    return subprocess.Popen(l, stdout=subprocess.PIPE, shell=True).stdout.read()
