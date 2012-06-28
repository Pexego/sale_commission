# Use a mako template with some sample data.
import re
import sys
import time

import openerprunbot.templates

if __name__ == "__main__":
    class RunBotBranch(object):
        """ Dummy Branch class to test mako templates. """
        project_name = 'server'
        unique_name = '~openerp-dev/openobject-server/trunk-dummy'
        merge_count = 1
        local_revision_count = 333
        overriden_repo_path = None
        overriden_project_name = None

    class Point(object):
        """ Dummy Point class to test mako templates. """
        state = 'running'
        test_base_result = True
        test_all_result = True
        job_id = 2
        subdomain = 'trunk_dummy_2'
        port = 22
        need_run_reason = ['server']
        manual_build = sys.maxint
        running_t0 = 100000
        repo_updates = [RunBotBranch()]
        version = 'trunk'

    class RunBotGroupedBranchBase(object):
        """ Dummy Group class to test mako templates. """
        name = 'trunk-dummy'
        team_name = 'openerp-dev'
        manual_build = sys.maxint
        wrong_matching = False
        points = [None, None, Point()]
        version = 'trunk'
        def repo_updates(selef):
            return [RunBotBranch()]

    class RunBot(object):
        """ Dummy RunBot class to test mako templates. """
        domain = 'runbotdev.openerp.com'
        number = 555
        workers = 666
        current_job_id = 777
        manual_build_count = 888
        server_net_port = 12000
        server_xml_port = 12100
        def nginx_index_time(self, t):
            return 'sometime'
        def available_workers(self):
            return 444
        def nginx_groups_sticky(self, team_name):
            return [RunBotGroupedBranchBase()]
        def nginx_groups_others(self, team_name):
            return []
        def nginx_groups_registered(self, team_name):
            return []
        def teams_with_branches(self):
            return ['openerp-dev']

    response = openerprunbot.templates.render_template('notice.html.mako',
        r=RunBot(), t=time.time(), re=re, team_name='openerp-dev', sys=sys, message="Hello")
    print response

