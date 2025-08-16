# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes instead of 30 seconds
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
