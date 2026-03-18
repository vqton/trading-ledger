"""Gunicorn configuration for production deployment."""
import os
import multiprocessing

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")

preload_app = True

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server")


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Gunicorn server")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn server is ready. Listening on: %s", bind)


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Gunicorn server is exiting")
