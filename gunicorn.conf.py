import os

bind = f"0.0.0.0:{os.environ.get('PORT', '4000')}"
workers = int(os.environ.get("GUNICORN_WORKERS", "4"))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
worker_class = "gthread"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
