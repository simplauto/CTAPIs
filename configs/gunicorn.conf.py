# Configuration Gunicorn pour API UTAC-OTC
# Documentation: https://docs.gunicorn.org/en/stable/settings.html

# Binding
bind = "0.0.0.0:5000"

# Workers
workers = 4  # Ajustez selon vos ressources (CPU cores * 2 + 1)
worker_class = "sync"
worker_connections = 1000
threads = 1

# Timeouts
timeout = 120           # Timeout général
graceful_timeout = 60   # Temps pour arrêter proprement
keepalive = 5          # Keep-alive timeout

# Requests
max_requests = 1000           # Redémarrer worker après N requêtes
max_requests_jitter = 100     # Ajouter randomness pour éviter thundering herd

# Application
preload_app = True      # Charger l'app avant de forker
daemon = False          # Ne pas daemoniser (géré par systemd)

# Process management
pidfile = "/home/utac-api/utac-api/logs/gunicorn.pid"
tmp_upload_dir = "/tmp"

# Logging
accesslog = "/home/utac-api/utac-api/logs/access.log"
errorlog = "/home/utac-api/utac-api/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Sécurité
user = "utac-api"
group = "utac-api"
umask = 0o027

# Performance
enable_stdio_inheritance = True

# Environment variables
raw_env = [
    'LANG=en_US.UTF-8',
    'LC_ALL=en_US.UTF-8',
    'PYTHONPATH=/home/utac-api/utac-api',
]

# Hooks pour personnaliser le comportement
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting API UTAC-OTC...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading API UTAC-OTC...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned successfully (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")