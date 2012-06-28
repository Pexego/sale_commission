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

runbot_state_lock = threading.Lock()

httpd = None

def serve(port):
    """ Serve HTTP requests via werkzeug development server.

    If werkzeug can not be imported, we fall back to wsgiref's simple_server.

    Calling this function is blocking, you might want to call it in its own
    thread.
    """

    global httpd

    interface = '127.0.0.1'
    try:
        import werkzeug.serving
        httpd = werkzeug.serving.make_server(interface, port, application, threaded=True)
        print 'HTTP service (werkzeug) running on %s:%s' % (interface, port)
    except ImportError, e:
        import wsgiref.simple_server
        httpd = wsgiref.simple_server.make_server(interface, port, application)
        print 'HTTP service (wsgiref) running on %s:%s' % (interface, port)

    httpd.serve_forever()

def start_server(port):
    """ Call serve() in its own thread.

    The WSGI server can be shutdown with stop_server() below.
    """
    threading.Thread(target=serve,args=(port,)).start()

def stop_server():
    """ Initiate the shutdown of the WSGI server.

    The server is supposed to have been started by start_server() above.
    """
    if httpd:
        httpd.shutdown()

def read_state():
    with runbot_state_lock:
        try:
            path = os.path.join('static', 'state.runbot')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    state = simplejson.loads(f.read())
                    pxgorunbot.state = state
        except Exception, e:
            print "Exception in read_state(): ", e

# TODO lock
def _with_state(f):
    state = {}
    path = os.path.join('static', 'state.runbot')

    with runbot_state_lock:
        if os.path.exists(path):
            with open(path, 'r') as h:
                state = simplejson.loads(h.read())

        f(state)

        with open(path, 'w') as h:
            data = simplejson.dumps(state, sort_keys=True, indent=4)
            h.write(data)

    # Replace the whole dictionary at once.
    pxgorunbot.state = state

def _stick(team, group):
    print 'stick', team, group
    def f(state):
        # TODO check team and group are valid
        state.setdefault(team, {})
        state[team].setdefault(group, {})
        state[team][group]['sticky'] = True
    _with_state(f)

def _unstick(team, group):
    print 'unstick', team, group
    def f(state):
        # TODO check team and group are valid
        state.setdefault(team, {})
        state[team].setdefault(group, {})
        if 'sticky' in state[team][group]:
            del state[team][group]['sticky']
        if not state[team][group]:
            del state[team][group]
        if not state[team]:
            del state[team]
    _with_state(f)

def _build(team, group):
    print 'build', team, group
    pxgorunbot.queue.put(('build', (team, group)))

def _register_branch(team, project, group):
    print 'register branch', team, project, group
    def f(state):
        # TODO check team and group are valid
        state.setdefault('registered-branches', [])
        state['registered-branches'].append("~%s/%s/%s" % (team, project, group))
    _with_state(f)

def _register_project(project):
    print 'register project'
    def f(state):
        # TODO check project is valid
        state.setdefault('registered-projects', []) # TODO must be a {}
        state['registered-projects'].append(project)
    _with_state(f)

def _configure_group(project_name=None, name=None, version=None, server_branch=None,
        client_web_branch=None, web_branch=None, addons_branch_0=None,
        addons_branch_1=None, addons_branch_2=None, modules=None):
    print 'configure group'
    addons_branches = []
    for i in (addons_branch_0, addons_branch_1, addons_branch_2):
        if i:
            addons_branches.append(i)
    def f(state):
        # TODO check project is valid
        state.setdefault('configured-branches', {})
        state['configured-branches'].setdefault(project_name, {})
        state['configured-branches'][project_name].setdefault(name, {})
        state['configured-branches'][project_name][name] = dict(
            version=version,
            server_branch=server_branch,
            client_web_branch=client_web_branch,
            web_branch=web_branch,
            addons_branches=addons_branches,
            modules=modules,
        )
    _with_state(f)


def application(environ, start_response):
    def send_notice(message):
        response = pxgorunbot.templates.render_template('notice.html.mako', message=message)
        start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', str(len(response)))])
        return [response]

    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO'] == ('/a/branch'):
        length = int(environ['CONTENT_LENGTH'])
        data = urllib.unquote(environ['wsgi.input'].read(length))
        data_ = urlparse.parse_qs(data).get('branch-input',[''])[0]
        m = pxgorunbot.branch_input_re.match(data_)
        if m:
            project_name = m.group(1)
            project = m.group(2)
            branch_name = m.group(3)
            _register_branch(project_name, project, branch_name)
            response = data_ + ' is registered. It will be picked by the Runbot at the next build iteration (about every two minutes).'
            return send_notice(response)

    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO'] == ('/a/project'):
        length = int(environ['CONTENT_LENGTH'])
        data = urllib.unquote(environ['wsgi.input'].read(length))
        data_ = urlparse.parse_qs(data).get('project-input',[''])[0]
        if data_:
            _register_project(data_)
            response = data_ + ' is registered. It will be picked by the Runbot at the next build iteration (about every two minutes).'
            return send_notice(response)

    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO'] == ('/a/configure-build'):
        length = int(environ['CONTENT_LENGTH'])
        data = urllib.unquote(environ['wsgi.input'].read(length))
        data_ = {}
        for n in (
            "project_name", "name", "version", "server_branch",
            "client_web_branch", "web_branch",
            "addons_branch_0", "addons_branch_1", "addons_branch_2", "modules"):
            data_[n] = urlparse.parse_qs(data).get(n,[''])[0]
        if (data_['version'] == 'trunk' or data_['version'] == '6.0') and \
            data_['project_name'] and \
            data_['name'] and \
            data_['server_branch'] and \
            (data_['web_branch'] or data_['client_web_branch']) and \
            data_['addons_branch_0']:
            _configure_group(**data_)
            response = data_['name'] + ' is registered. It will be picked by the Runbot at the next build iteration (about every two minutes).'
            return send_notice(response)

    # TODO must be a POST instead of a GET
    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO'] == ('/a'):
        query = urlparse.parse_qs(environ['QUERY_STRING'])

        if query.get('project'):
            project = query['project'][0]

            if query.get('build'):
                group = query['build'][0]
                _build(project, group)
                response = '`' + group + '` will be built.'
                return send_notice(response)

    message = 'Are you lost?\n\n\n(^____^)\n'
    response = pxgorunbot.templates.render_template('notice.html.mako', message=message)
    start_response('404 Not Found', [('Content-Type', 'text/html'), ('Content-Length', str(len(response)))])
    return [response]

if __name__ == '__main__':
   serve(8999)


