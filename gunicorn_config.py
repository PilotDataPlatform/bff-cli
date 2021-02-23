workers = 4
threads = 2
bind = '0.0.0.0:5078'
daemon = 'false'
worker_connections = 1200
accesslog = 'gunicorn_access.log'
errorlog = 'gunicorn_error.log'
loglevel = 'debug'
