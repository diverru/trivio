bind = '0.0.0.0:8000'
workers = 2
name = "trivio_backend"
user = "nobody"
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/gunicorn.log"
