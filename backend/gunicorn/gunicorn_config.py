import logging

import gunicorn

gunicorn.SERVER = "Webserver"
bind = "0.0.0.0"
gunicorn.SERVER_PORT = 8080
gunicorn.SERVER_NAME = "Gunicorn Server"
gunicorn.SERVER_SOFTWARE = "Webserver"

pidfile = "/var/run/gunicorn.pid"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "debug"
access_log_format = '%(h)s - %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%(L)s"'
formatter = logging.Formatter(access_log_format)
