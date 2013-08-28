# -*- coding: utf-8 -*-
import ConfigParser
import os
import re
import subprocess
import sys
import threading
import time
import traceback
import copy
import models
from app import app

import pxgorunbot
from pxgorunbot.misc import *

vcs_file = ConfigParser.ConfigParser()
vcs_file.read(os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'config/vcs.conf'))

extensions_file = ConfigParser.ConfigParser()
extensions_file.read(os.path.join(os.path.dirname(sys.modules['__main__'].__file__),'config/extensions.conf'))

POINTS = 5

def underscore(s):
    return s.replace("~","").replace(":","_").replace("/","_").replace(".","_").replace(" ","_")

def process_command(command):
    if '|' not in command:
        log("Exceptions: Command misformatted %s" % command)
        return False

    return command.split('|')

def has_test_enable_flag(server_bin_path):
    p1 = subprocess.Popen([server_bin_path, "--help"],
        stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "test-enable"], stdin=p1.stdout,
        stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()[0]
    return output == "    --test-enable       Enable YAML and unit tests.\n"

class Job(object):
    """
    A Job encapsulates all the necessary data to build a branch group for a
    given slot. The build is done in its own worker thread.
    """

    def __init__(self, project, port, test, job_id, debug, project_name, db_path=None, custom_addons=[], modules=None):
        self.project = project
        self.job_id = job_id
        self.name = project_name
        self.version = project.version
        self.debug = debug
        self.db_path = db_path
        
        self.repo_updates = project.repo_updates()
        self.port = port
        self.test = test
        self.running_server_pid = 0
        self.client_web_pid = 0
        self.running_t0=0

        repo = os.path.join(project.runbot.wd,'repo')
        repo = os.path.join(repo, project_name)
        self.server_path = project.server.path
        self.client_web_path = project.client_web.path if project.client_web else None
        self.web_src = project.web.path if project.web else None

        # if addons is not the full addons branch use trunk
        if custom_addons:
            self.addons_src = [a.path for a in project.runbot_addons if not a.custom and not a.brancheable] + custom_addons
        else: 
            self.addons_src = [a.path for a in project.runbot_addons]

        # Running path <Root>/static/<domain>
        self.subdomain = "%s-%s"%(self.name.replace('_','-').replace('.','-'),self.job_id)
        self.running_path = os.path.join(project.runbot.wd,'static',self.subdomain)
        self.log_path = os.path.join(self.running_path,'logs')
        self.flags_path = os.path.join(self.running_path,'flags')

        #server
        self.server_bin_path=os.path.join(self.server_path,"openerp-server")
        self.server_log_path=os.path.join(self.log_path,'server.txt')
        self.server_log_base_path=os.path.join(self.log_path,'test-base.txt')
        self.server_log_all_path=os.path.join(self.log_path,'test-all.txt')

        # coverage
        self.coverage_file_path=os.path.join(self.log_path,'coverage.pickle')
        self.coverage_base_path=os.path.join(self.log_path,'coverage-base')
        self.coverage_all_path=os.path.join(self.log_path,'coverage-all')

        # Web60
        self.client_web_pid=None
        if self.client_web_path:
            self.client_web_bin_path=os.path.join(self.client_web_path,"openerp-web.py")
            self.client_web_doc_path=os.path.join(self.client_web_path,"doc")
            self.client_web_log_path=os.path.join(self.log_path,'client-web.txt')

        # test
        self.test_base_result=None
        self.test_base_path=os.path.join(self.log_path,'test-base.txt')
        self.test_all_result=None
        self.test_all_path=os.path.join(self.log_path,'test-all.txt')

        self.server_net_port=project.runbot.server_net_port
        self.server_xml_port=project.runbot.server_xml_port
        self.client_web_port=project.runbot.client_web_port

        if self.name != self.project.name:
            self.db = self.name + '_' + str(self.job_id) + "_test_" + self.project.name
            self.db_all = "%s_all" % self.db
        else:
            self.db = self.name + '_' + str(self.job_id)
            self.db_all = "%s_all" % self.db

        self.download_src = project.runbot_downloads and project.runbot_downloads[0].path or False
        self.modules = modules
        
        for i in [self.running_path,self.log_path,self.flags_path]:
            if not os.path.exists(i):
                os.makedirs(i)
                
        self.update_job()
        
    def update_job(self):
        self.start_time = 0
        self.completed_time = 0
        self.completed = False
        
        if self.version not in ["6.0","5.0"]:
            self.addons_path = self.fill_addons_path()
        else:
            self.addons_path = False
            self.link_addons()

    def link_addons(self):
        addons_path_root = os.path.join(self.server_path,"bin/addons")
        for addons_path in self.addons_src:
            for module in os.listdir(addons_path):
                run(["ln","-s",os.path.join(addons_path,module),addons_path_root])
         
        if self.download_src:
            for download_module in os.listdir(self.download_src):
                run(["ln","-s",os.path.join(self.download_src,download_module),addons_path_root])


    def fill_addons_path(self):
        addons_path = []
        if self.web_src:
            addons_path.append(self.web_src + "/addons")
        addons_path.extend(self.addons_src)
        if self.download_src:
            addons_path.append(self.download_src)
        return addons_path

    def spawn(self):
        log("runbot-spawn-worker-" + str(self.job_id), project=self.name)
        t = threading.Thread(target=self.work, name=('runbot-group-worker-' + str(self.job_id)))
        t.daemon = True
        t.start()

    def work(self):
        try:
            #self.project.pull_branches()
            self.start_time = time.time()
            self.start()
            self.completed_time = time.time()
            self.completed = True
            log("runbot-end-worker", job=self.name)
        except Exception, e:
            self.completed = True
            log("runbot-end-worker [with exception]", job=self.name)

    def start_createdb(self):
        run(["psql","template1","-c","select pg_terminate_backend(procpid) from pg_stat_activity where datname in ('%s','%s')"%(self.db,self.db_all)])
        time.sleep(3)
        run(["dropdb",self.db])
        run(["dropdb",self.db_all])
        run(["createdb",self.db])
        run(["createdb",self.db_all])

    def run_log(self, cmd, logfile, env=None):
        env = dict(os.environ, **env) if env else None
        log("run", *cmd, logfile=logfile)
        out=open(logfile,"w")
        p=subprocess.Popen(cmd, stdout=out, stderr=out, close_fds=True, env=env)
        self.running_server_pid=p.pid
        p.communicate()
        return p

    def resolve_server_bin_path(self):
        # This can be done only if the files are present otherwise the if
        # will always fail. Alternatively, server_bin_path could be a property.
        if not os.path.exists(self.server_bin_path): # for 6.0 and 5.0 branches
            self.server_bin_path=os.path.join(self.server_path,"bin","openerp-server.py")

    def start_test_base(self):
        log("job-start-server-base")
        cmd = [self.server_bin_path,"-d",self.db,"-i","base","--stop-after-init","--no-xmlrpc","--no-netrpc"]
        if self.version != '5.0':
            cmd.extend(["--no-xmlrpcs","--log-level=test"])
        if self.addons_path:
            cmd.append("--addons-path=" + ",".join(self.addons_path))
            
        _has_test_enable_flag = False
        if has_test_enable_flag(self.server_bin_path):
            cmd.append("--test-enable")
            _has_test_enable_flag = True
        cmd = ["coverage","run","--branch"] + cmd
        self.run_log(cmd, logfile=self.test_base_path,env={'COVERAGE_FILE': self.coverage_file_path})
        run(["coverage","html","-d",self.coverage_base_path,"--ignore-errors"],env={'COVERAGE_FILE': self.coverage_file_path})
        if _has_test_enable_flag:
            success_message = "openerp.modules.loading: Modules loaded."
            rc = not bool(run(["grep",success_message,self.test_base_path]))
        else:
            rc = bool(run(["grep","Traceback",self.test_base_path]))
        self.test_base_result = rc

    def start_test_all(self):
        log("job-start-server-all")
        if self.db_path:
            run(["psql","-d",self.db_all,"-f",self.db_path])
            cmd = [self.server_bin_path,"-d",self.db_all,"--update=all","--stop-after-init","--no-xmlrpc","--no-netrpc"]
        elif self.modules:
            cmd = [self.server_bin_path,"-d",self.db_all,"-i",self.modules,"--stop-after-init","--no-xmlrpc","--no-netrpc"]
        else:
            cmd = [self.server_bin_path,"-d",self.db_all,"-i","base,account,stock,mrp,sale,purchase,product","--stop-after-init","--no-xmlrpc","--no-netrpc"]
            
        if self.version != "5.0":
            cmd.extend(["--no-xmlrpcs","--log-level=test"])
            
        if self.addons_path:
            cmd.append("--addons-path=" + ",".join(self.addons_path))
        _has_test_enable_flag = False
        if has_test_enable_flag(self.server_bin_path):
            cmd.append("--test-enable")
            _has_test_enable_flag = True
        cmd = ["coverage","run","--branch"] + cmd
        self.run_log(cmd, logfile=self.test_all_path)
        run(["coverage","html","-d",self.coverage_all_path,"--ignore-errors","--include=*.py"])
        if _has_test_enable_flag:
            success_message = "openerp.modules.loading: Modules loaded."
            rc = not bool(run(["grep",success_message,self.test_all_path]))
        else:
            rc = bool(run(["grep","Traceback",self.test_all_path]))
        self.test_all_result = rc

    def start_server(self):
        port = self.port
        log("job-start-server",branch=self.name,port=port)
        cmd=[self.server_bin_path]
        if self.version != "5.0":
            cmd.extend(["--no-xmlrpcs","--netrpc-port=%d"%(self.server_net_port+port),"--xmlrpc-port=%d"%(self.server_xml_port+port)])
        else:
            cmd.extend(["--net_port=%d"%(self.server_net_port+port),"--port=%d"%(self.server_xml_port+port)])
        if self.addons_path:
            cmd.append("--addons-path=" + ",".join(self.addons_path))
        if os.path.exists(os.path.join(self.server_path, 'openerp', 'wsgi.py')) \
            or os.path.exists(os.path.join(self.server_path, 'openerp', 'wsgi', 'core.py')):
            cmd+=["--db-filter=%s_*" % self.name,"--load=web"]
        log("run",*cmd,log=self.server_log_path)
        out=open(self.server_log_path,"w")
        p=subprocess.Popen(cmd, stdout=out, stderr=out, close_fds=True)
        self.running_server_pid=p.pid

    def start_client_web(self):
        if not self.client_web_path:
            return
        port = self.port
        log("job-start-client-web",branch=self.name,port=port)
        config="""
        [global]
        server.environment = "development"
        server.socket_host = "0.0.0.0"
        server.socket_port = %d
        server.thread_pool = 10
        tools.sessions.on = True
        log.access_level = "INFO"
        log.error_level = "INFO"
        tools.csrf.on = False
        tools.log_tracebacks.on = False
        openerp.server.host = 'localhost'
        openerp.server.port = '%d'
        openerp.server.protocol = 'socket'
        openerp.server.timeout = 450
        [openerp]
        host = 'localhost'
        port = '%d'
        protocol = 'socket'
        [openerp-web]
        #dblist.filter = 'BOTH'
        dbbutton.visible = True
        company.url = ''
        """%(self.client_web_port+port,self.server_net_port+port,self.server_net_port+port)
        config=config.replace("\n        ","\n")
        cfgs = [os.path.join(self.client_web_path,"doc","openerp-web.cfg"), os.path.join(self.client_web_path,"openerp-web.cfg")]
        if os.path.exists(os.path.join(self.client_web_path,"config")):
            cfgs.append(os.path.join(self.client_web_path,"config","openerp-web.cfg"))
        for i in cfgs:
            f=open(i,"w")
            f.write(config)
            f.close()

        cmd=[self.client_web_bin_path]
        log("run",*cmd,log=self.client_web_log_path)
        out=open(self.client_web_log_path,"w")
        p=subprocess.Popen(cmd, stdout=out, stderr=out, close_fds=True)
        self.client_web_pid=p.pid

    def start(self):
        log("job-start",branch=self.name,port=self.port)
        #.start_rsync()
        self.stop()
        self.resolve_server_bin_path()
        self.start_createdb()
        try:
            if self.test:
                self.start_test_base()
                if not self.debug:
                    self.start_test_all()
                else:
                    self.test_all_result = True
            self.start_server()
            self.start_client_web()
        except OSError,e:
            log("branch-start-error",exception=e)
        except IOError,e:
            log("branch-start-error",exception=e)
        self.running_t0=time.time()
        log("branch-started",branch=self.name,port=self.port)

    def stop(self):
        log("Stopping job", id=self.job_id, branch=self.name)
        if self.running_server_pid:
            kill(self.running_server_pid)
        if self.client_web_pid:
            kill(self.client_web_pid)


class Point(object):
    """A point is a build slot and associated to a worker thread."""
    def __init__(self, project, job):
        """Create a Point from a given group and job."""
        self.version = project.version
        self.project_name  = project.name
        self.port = job.port
        self.job_id = job.job_id
        self.db = job.db
        self.running_path = job.running_path
        self.subdomain = job.subdomain
        self.need_run_reason = project.need_run_reason

        self.update(job)
        self.manual_build = project.manual_build

    def update(self, job):
        """
        Update the Point from a job. The job should be the same than the one
        used in `__init__()`.
        """
        self.state = 'running' if job.completed else 'testing'
        self.running_t0 = job.running_t0
        self.test_base_result = job.test_base_result
        self.test_all_result = job.test_all_result

class RunbotDownload(object):

    def __init__(self, command, path):
        self.path = path
        self.file_path = False
        self.command = command

        self.download_module()

    def download_module(self):
        file_name = self.command[1].split(os.sep)[-1]
        file_extension = file_name.split(".")[-1]
        #FIXME
        run("cd " + self.path + " && " + " ".join(self.command))
        cmd = extensions_file.get(file_extension, "cmd")
        self.file_path = os.path.join(self.path,file_name)
        if cmd:
            run("cd " + self.path + " && " + cmd.replace("file",file_name))


class RunbotBranch(object):

    def __init__(self, command, path, branch_type, project, custom=False, brancheable=False, branch_name=False):
        self.project = project
        self.vcs_type = command[0]
        self.branch = command[1]
        self.path = path
        self.branch_type = branch_type
        self.name = project.name + "_" + branch_type
        self.revision = 0
        self.commiter = False
        self.custom = custom
        self.brancheable = brancheable
        self.branches = []
        self.branch_name = branch_name

        self.pull_branch()

    def info(self):
        if "info" in vcs_file.options(self.vcs_type):
            info_cmd =  vcs_file.get(self.vcs_type, "info")
            return run_output(self.vcs_type + " " + info_cmd + " " + self.path)
        else:
            return ""
            
    def checkout(self):
        if os.path.exists(self.path):
            cmd = "cd " + self.path + " && " + self.vcs_type + " " + vcs_file.get(self.vcs_type, "checkout").replace("branch", self.branch_name)
            run(cmd)     

    def pull_branch(self):
        if os.path.exists(self.path):
            cmd = "cd " + self.path + " && " + self.vcs_type + " " + vcs_file.get(self.vcs_type, "pull")
            #TODO: Quizás sea necesario un update
        else:
            cmd = self.vcs_type + " " + vcs_file.get(self.vcs_type, "clone") + " " + self.branch + " " + self.path

        run(cmd)

        revision = run_and_get("cd " + self.path + " && " + self.vcs_type + " " + vcs_file.get(self.vcs_type, "revision"))
        if revision != self.revision:
            self.commiter = run_and_get("cd " + self.path + " && " + self.vcs_type + " " + vcs_file.get(self.vcs_type, "committer"))
            self.revision = revision
            if self.name not in self.project.need_run_reason:
                self.project.need_run_reason.append(self.name)
            
        if self.branch_name:
            self.checkout()
            
    def get_branches(self):
        if os.path.exists(self.path) and self.brancheable:
            cmd = "cd " + self.path + " && " + self.vcs_type + " " + vcs_file.get(self.vcs_type, "branches")
            branches = run_and_get(cmd)
            return [x for x in branches.split("\n") if x]
        return []
        

class RunbotProject(object):

    def __init__(self,project,runbot,server_branch,client_web_branch=None,web_branch=None):
        self.db_project = project
        self.name = underscore(project.name)
        self.runbot = runbot
        self.version = project.version
        self.db_path = project.db_path

        self.server_branch = server_branch
        self.client_web_branch = client_web_branch
        self.web_branch = web_branch
        self.addons_branches = project.addons
        self.downloads_url = project.downloads
        self.runbot_downloads = []
        self.modules = project.modules
        
        
        self.server = None
        self.client_web = None
        self.web = None
        self.runbot_addons = []

        # A normal manual_build is maxint, a manual_build is used only when
        # manually requesting a build with a 'build' command pushed in the
        # queue. The value will be reset to maxint after the build is done.
        self.manual_build = sys.maxint
        self.need_run_reason = []
        self.points = [None for x in xrange(POINTS)]

    def add_point(self, j):
        assert not j.completed
        p = Point(self, j)
        self.points = self.points[1:] + [p] # TODO delete db and on-disk data

    def complete_point(self, j):
        assert j.completed
        for p in self.points + [None]:
            if p and p.job_id == j.job_id:
                break
        if p and p.state != 'running':
            p.update(j)

    def all_points_completed(self):
        for p in self.points:
            if p is not None and p.state != 'running':
                return False
        return True

    def repo_updates(self):
        r = []
        if self.server:
            r.append(copy.copy(self.server))
        for x in self.runbot_addons:
            r.append(copy.copy(x))
        if self.web:
            r.append(copy.copy(self.web))
        elif self.client_web:
            r.append(copy.copy(self.client_web))
        return r

    def is_ok(self):
        """
        Test whether the group is useable, i.e. if self.populate_branches()
        didn't early return.
        """
        if self.server and (self.web or self.client_web) and self.runbot_addons:
            return True
        else:
            return False

    def create_project(self):
        log("runbot-create-project")
        repo = os.path.join(self.runbot.wd, 'repo')
        if not os.path.exists(repo+'/'+self.name):
            os.mkdir(repo+'/'+self.name)
        repo = os.path.join(repo, self.name)
        if not self.server:
            path = os.path.join(repo, '__configured_' + self.name + '_server')
            self.server = RunbotBranch(self.server_branch, path, "server", self)
        else:
            self.server.pull_branch()

        if self.client_web_branch:
            if not self.client_web:
                path = os.path.join(repo, '__configured_' + self.name + '_web')
                self.client_web = RunbotBranch(self.client_web_branch, path, "client_web", self)
            else:
                self.client_web.pull_branch()
        else:
            self.client_web = None

        if self.web_branch:
            if not self.web:
                path = os.path.join(repo, '__configured_' + self.name + '_web')
                self.web = RunbotBranch(self.web_branch, path, "web", self)
            else:
                self.web.pull_branch()
        else:
            self.web = None

        for addons_branch in self.addons_branches:
            path = os.path.join(repo, '__configured_' + self.name + '_addons_' + str(addons_branch.number))
            if (self.name + "_addons_" + str(addons_branch.number)) not in [b.name for b in self.runbot_addons]:
                branch = RunbotBranch(process_command(addons_branch.repo), path, "addons_" + str(addons_branch.number), self, addons_branch.custom, addons_branch.brancheable)
                self.runbot_addons.append(branch)
                
                if branch.brancheable:
                    branches = branch.get_branches()
                    for repo_branch in branches:
                        if repo_branch != vcs_file.get(branch.vcs_type, "default_branch"):
                            if (self.name + "_branch_" + repo_branch) not in branch.branches:
                                path = os.path.join(repo, '__configured_' + self.name + '_addons_' + str(addons_branch.number) + "_branch_" + repo_branch)
                                branch.branches.append(RunbotBranch(process_command(addons_branch.repo), path, "branch_" + repo_branch, self, addons_branch.custom, branch_name=repo_branch))
                            else:
                                for branch in branch.branches:
                                    if branch.name == (self.name + "_branch_" + repo_branch):
                                        branch.pull_branch()
                                        break
            else:
                for branch in self.runbot_addons:
                    if branch.name == (self.name + "_addons_" + str(addons_branch.number)):
                        branch.pull_branch()
                        break

        if self.downloads_url:
            path = os.path.join(repo, '__configured_' + self.name + '_extra_modules')
            if not os.path.exists(path):
                os.mkdir(path)
        for module in self.downloads_url:
            if module.command not in [b.command for b in self.runbot_downloads]:
                self.runbot_downloads.append(RunbotDownload(process_command(module.command), path))
                module.path = path
                module.save()
                  


class RunBot(object):
    """Used as a singleton, to manage almost all the Runbot state and logic."""
    def __init__(self, wd, server_net_port, server_xml_port,
        client_web_port,  number, flask_port, test,
        current_job_id, debug):
        self.wd=os.path.abspath(wd)
        self.server_net_port=int(server_net_port)
        self.server_xml_port=int(server_xml_port)
        self.client_web_port=int(client_web_port)
        self.number=int(number)
        self.flask_port=int(flask_port)
        self.test=int(test)
        self.projects = []
        self.allocated_port = 0
        self.jobs = {}
        self.current_job_id = current_job_id
        self.debug = debug
        self.manual_build_count = 0
        
        self.my_domain = app.config.get('MY_DOMAIN')

    def populate_projects(self):
        for project in models.Project.select():
            server_branch = False
            client_web_branch = False
            web_branch = False
            server_branch = process_command(project.server)
            if project.web_client:
                client_web_branch = process_command(project.web_client)
            elif project.openerp_web:
                web_branch = process_command(project.openerp_web)
            if underscore(project.name) not in [x.name for x in self.projects]:
                p = RunbotProject(project,self,server_branch,client_web_branch,web_branch)
                self.projects.append(p)
            else:
                for runbot_project in self.projects:
                    if runbot_project.name == underscore(project.name):
                        p = runbot_project
                        break
            p.create_project()


    def fetch_projects(self):
        self.populate_projects()

        log("runbot-run-group", projects=len(self.projects))
        return self.projects
    
    def flask_projects_development(self,project_name):
        gs = [(g.name,g) for g in self.projects if g.name==project_name]
        gs.sort()
        return [g for (x,g) in gs]
    
    def flask_projects(self):
        return pxgorunbot.templates.render_template('index.html.mako',
            r=self,t=time.time(),re=re)

    def projects_with_branches(self):
        ps = [p.name for p in self.projects]
        ps = list(set(ps))
        ps.sort()
        return ps

    def flask_index_time(self,t):
        for m,u in [(86400,'d'),(3600,'h'),(60,'m')]:
            if t>=m:
                return str(int(t/m))+u
        return str(int(t))+"s"

    def flask_index(self, project_name):
        return pxgorunbot.templates.render_template('branches.html.mako',
            r=self, t=time.time(), re=re, project_name=project_name, sys=sys)
    
        
    def urls_config(self):
        return pxgorunbot.templates.render_template('urls.conf.mako',r=self)

    def flask_reload(self):
        try:
            f = open(os.path.join(self.wd,'urls.conf'),"w")
            content = self.urls_config()
            f.write(content)
        except Exception, e:
            log("WARNING: exception when templating urls.conf:")
            if f: f.close()

    def flask_update(self):
        try:
            f = None
            f = open(os.path.join(self.wd,'static','index.html'),"w")
            content = self.flask_projects()
            f.write(content)
        except Exception, e:
            log("WARNING: excepneed_run_reasontion when templating index.html:")
            if f: f.close()
        for project_name in self.projects_with_branches():
            try:
                f = None
                fn = project_name + '.html'
                f = open(os.path.join(self.wd,'static',fn),"w")
                content = self.flask_index(project_name)
                f.write(content)
            except Exception, e:
                log("WARNING: exception when templating %s:" % fn)
                if f: f.close()
                break

        self.flask_reload()

    def process_command_queue(self):
        while not pxgorunbot.queue.empty():
            command, params = pxgorunbot.queue.get()
            if command == 'build':
                project_name = params
                if project_name in self.projects and self.projects[self.projects.index(project_name)].manual_build == sys.maxint:
                    self.manual_build_count += 1
                    self.projects[self.projects.index(project_name)].manual_build = self.manual_build_count
                    self.projects[self.projects.index(project_name)].need_run_reason.append('build')
            else:
                log("WARNING: unknown command", command)

    def reset_build_numbers(self):
        self.projects.sort()
        ps = [x for x in self.projects]
        self.manual_build_count = 0
        for p in ps:
            if p.manual_build == sys.maxint:
                break
            self.manual_build_count += 1
            p.manual_build = self.manual_build_count

    def allocate_port(self):
        if self.allocated_port > self.number * 2:
            self.allocated_port = 0
        self.allocated_port += 1
        return self.allocated_port

    def run_projects(self):
        res = True
        for p in self.projects:

            if len(self.jobs) > self.number:
                res = False
                break
                
            # Don't run multiple jobs at the same time for the same group.
            if p.need_run_reason and p.all_points_completed():
                manage = False
                p.need_run_reason = []
                p.manual_build = sys.maxint
                for job in self.jobs.values():
                    if job.name == p.name:
                        job.update_job()
                        for point in p.points:
                            if point is not None:
                                point.update(job) 
                        job.spawn()
                        manage = True
                if not manage:
                    port = self.allocate_port()
                    self.current_job_id += 1
                    job = Job(p, port, self.test, self.current_job_id, self.debug, p.name, db_path=p.db_path, custom_addons=[a.path for a in p.runbot_addons if a.custom], modules=p.modules) 
                    p.add_point(job)
                    p.need_run_reason = []
                    p.manual_build = sys.maxint
                    self.jobs[job.job_id] = job
                    job.spawn()
                    
                    if p.db_project.to_test:
                        port = self.allocate_port()
                        self.current_job_id += 1
                        p_to_test = False
                        for runbot_project in self.projects:
                            if runbot_project.name == underscore(p.db_project.to_test.name):
                                p_to_test = runbot_project
                                break
                        
                        if p_to_test:
                            job = Job(p_to_test, port, self.test, self.current_job_id, self.debug, p.name, db_path=p.db_path, custom_addons=[a.path for a in p.runbot_addons if a.custom], modules=p.modules)
                            p.add_point(job)
                            self.jobs[job.job_id] = job
                            job.spawn()
                    for project_branch in p.runbot_addons:
                        for repo_branch in project_branch.branches:
                            port = self.allocate_port()
                            self.current_job_id += 1
                            job = Job(p, port, self.test, self.current_job_id, self.debug, p.name, db_path=p.db_path, custom_addons=[repo_branch], modules=p.modules)
                            p.add_point(job)
                            self.jobs[job.job_id] = job
                            job.spawn()
                        
        return res
                
    def complete_jobs(self):
        """Update all slots with the completed jobs."""
        for job in self.jobs.values():
            if job.completed:
                for p in self.projects:
                    if p.name == job.name:
                        p.complete_point(job)
                        break

    def reap_oldest_job(self):
        """Kill some job to limit the number of processes."""
        if len(self.jobs) > self.number:
            victim = None
            for job in self.jobs.itervalues():
                if not victim or job.job_id < victim.job_id:
                    victim = job
            if victim:
                victim.stop()
                del self.jobs[victim.job_id]


    def loop(self):
        """
        Repeatedly fetch branch information from Launchpad, run jobs, update
        HTML pages, ...
        """
        while 1:
            try:
                while True: # 2 minutes
                    try: # Make sure time.sleep() is always called.
                        self.fetch_projects()
                        self.process_command_queue()
                        res = self.run_projects()
                        self.complete_jobs()
                        self.reap_oldest_job()
                        self.reset_build_numbers()
                        if res:
                            self.flask_update()
                        #for p in self.projects:
                        #    p.update_state(openerprunbot.state)
                    except Exception, e:
                        log("WARNING: exception:")
                    time.sleep(20)
            except KeyboardInterrupt,e:
                log("SIGINT received, exiting...")
                pxgorunbot.server.stop_server()
                for i in self.jobs.values():
                    i.stop()
                break

