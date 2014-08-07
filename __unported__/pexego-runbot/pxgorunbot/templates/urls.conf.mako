[instances]
% for p in r.projects:
% for i in p.points:
% if i:
% if i.version in ['6.0','5.0']:
${i.job_id}:http://${r.my_domain}:${r.client_web_port+i.port}
% else:
${i.job_id}:http://${r.my_domain}:${r.server_xml_port+i.port}
% endif
% endif
% endfor
% endfor
