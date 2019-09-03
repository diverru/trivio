bind = '0.0.0.0:8000'
workers = 2
name = "trivio_backend"
user = "nobody"
loglevel = "info"
accesslog = "/var/www/logs/access.log"
errorlog = "/var/www/logs/gunicorn.log"
