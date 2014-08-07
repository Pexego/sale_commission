<%def name="point_(r,g,p)">
          <td id="${p.job_id}">
            <span class="i action-toggle dropdown-toggle" data-toggle="dropdown">B</span>
    <ul class="dropdown-menu">
        <li><a href="/static/${p.subdomain}/logs/test-all.txt">
        % if p.test_all_result==False:
            Install logs (failure)
        % elif p.test_all_result==True:
            Install logs (success)
        % else:
            Install logs (ongoing)
        % endif
        </a></li>
        <li><a target="_blank" href="/static/${p.subdomain}/logs/coverage-all/index.html">Code coverage</a></li>
        <li><a target="_blank" href="/static/${p.subdomain}/logs/server.txt">Server logs</a></li>
        <li><a target="_blank" href="/static/${p.subdomain}/logs/client-web.txt">Web logs</a></li>
        <li>NET-RPC port: ${r.server_net_port+p.port}</li>
        <li>XML-RPC port: ${r.server_xml_port+p.port}</li>
        % if 'build' in p.need_run_reason:
          <li>(Build manually requested)</li>
        % endif
        % if p.manual_build != sys.maxint:
              <li>(${p.manual_build})</li>
        % endif
    </ul>
% if p.state == 'testing':
            <p><span class="status"> </span>
% elif p.test_base_result==True and p.test_all_result==True:
            <p><span class="status green"> </span>
% elif p.test_base_result==False or p.test_all_result==False:
            <p><span class="status red"> </span>
% else:
            <p><span class="status"> </span>
% endif
% if p.state == 'testing':
        <span class="testing">Testing...</span></p>
% elif p.running_t0 and p.test_all_result:
        <span class="running-long">Age: ${r.flask_index_time(t-p.running_t0)}</span></p>
% elif p.running_t0:
        <span class="testing">Age: ${r.flask_index_time(t-p.running_t0)}</span></p>
% else:
        <span class="testing">Internal error</span></p>
% endif
<a href="#${p.job_id}">(Build ${p.job_id})</a>
% if ((p.job_id > r.current_job_id - r.number) and p.running_t0):
    <form target="_blank" method="GET" action="/openerp/${p.job_id}">
        <button type="submit">Connect</button>
    </form>
% else:
            <p><button disabled="disabled">Disabled</button></p>
% endif
          </td>
</%def>

<%def name="branch_(r,g,b)">
<span class="label notice">
${b.name}
</span>
</%def>

<%def name="short_row_(r,g)">
        <tr>
          <th>
            <p>${g.name}</p>
% for b in g.repo_updates():
    ${branch_(r,g,b)}
% endfor
          </th>
% for p in reversed(g.points):
%   if p:
      ${point_(r,g,p)}
%   else:
      <td></td>
%   endif
% endfor
        </tr>
</%def>

