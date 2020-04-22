server {
  listen 8080;
  server_name yocto.mirror.com;
    
  access_log /var/log/nginx/yocto-mirror-access.log;
  error_log /var/log/nginx/yocto-mirror-error.log;

  location ~ ^/(images|javascript|js|css|media|static|statics)/  {
    root   /var/www;
    expires 30d;
  }

  try_files  $uri @cgit;
  location @cgit {
    include /etc/nginx/fastcgi_params;
    fastcgi_param PATH_INFO    $uri;
    fastcgi_param QUERY_STRING $args;
    fastcgi_param HTTP_HOST    $server_name;
    fastcgi_param SCRIPT_FILENAME /usr/lib/cgit/cgit.cgi;
    fastcgi_pass unix:/run/fcgiwrap.socket;
  }
}
