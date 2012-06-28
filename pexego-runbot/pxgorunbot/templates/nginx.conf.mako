pid nginx/nginx.pid;
worker_processes  1;
events { worker_connections  1024; }
http {
  include /etc/nginx/mime.types;
  error_log nginx/error.log;
  access_log nginx/access.log;
  server_names_hash_max_size 512;
  server_names_hash_bucket_size 256;
  autoindex on;
  client_body_temp_path nginx; proxy_temp_path nginx; fastcgi_temp_path nginx; index index.html;
  server { listen ${r.nginx_port} default; server_name ${r.domain}; root static;
     location /a { proxy_pass http://127.0.0.1:${r.nginx_port - 1}; 
                    proxy_set_header X-Forwarded-Host $host;}
  }
  % for p in r.projects:
  % for i in p.points:
  % if i:
     server  {  listen ${r.nginx_port}; server_name ${p.name}.${r.domain}_${i.job_id};
        location / {
                % if i.version == '6.0':
                   proxy_pass http://127.0.0.1:${r.client_web_port+i.port};
                % else:
                   proxy_pass http://127.0.0.1:${r.server_xml_port+i.port}; 
                % endif
                   #proxy_set_header X-Forwarded-Host $host;
                   proxy_set_header Host $http_host;}
            }
  % endif
  % endfor
  % endfor
}
