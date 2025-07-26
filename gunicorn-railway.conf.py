# Configuration Gunicorn pour Railway
# Optimisée pour l'environnement cloud Railway

import os

# Port dynamique fourni par Railway
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Workers - Railway recommande 1-2 workers pour les petites instances
workers = int(os.environ.get("WEB_CONCURRENCY", 2))
worker_class = "sync"
worker_connections = 1000

# Timeouts - Configuration Railway-friendly
timeout = 120
graceful_timeout = 60
keepalive = 5

# Requests
max_requests = 1000
max_requests_jitter = 100

# Application
preload_app = True
daemon = False

# Logging - Railway capture automatiquement stdout/stderr
loglevel = os.environ.get("LOG_LEVEL", "info")
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Format de log optimisé pour Railway
access_log_format = '%(h)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Performance pour Railway
enable_stdio_inheritance = True
pythonpath = "."

# Hooks spécifiques Railway
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting API UTAC-OTC on Railway...")
    server.log.info(f"⚡ Workers: {workers}, Port: {port}")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading API UTAC-OTC on Railway...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("⚠️ Worker received shutdown signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"👷 Spawning worker {worker.age}")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"✅ Worker {worker.pid} ready")

# Variables d'environnement Railway
raw_env = [
    f'PORT={port}',
    'PYTHONUNBUFFERED=1',
    'FLASK_ENV=production',
]