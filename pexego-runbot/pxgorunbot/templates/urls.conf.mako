[instances]
% for p in r.projects:
% for i in p.points:
% if i:
% if i.version == '6.0':
${i.job_id}:http://127.0.0.1:${r.client_web_port+i.port}
% else:
${i.job_id}:http://127.0.0.1:${r.server_xml_port+i.port}
% endif
% endif
% endfor
% endfor
