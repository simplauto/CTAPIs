#!/bin/bash

# =================================================================
# Script d'installation automatique - API UTAC-OTC
# Compatible Ubuntu 20.04/22.04 - VPS OVH, Digital Ocean, etc.
# =================================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage coloré
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_requirements() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Ubuntu
    if ! grep -q "Ubuntu" /etc/os-release; then
        log_warning "Ce script est optimisé pour Ubuntu. Voulez-vous continuer ? (y/n)"
        read -r response
        if [[ ! $response =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Vérifier les droits sudo
    if ! sudo -n true 2>/dev/null; then
        log_error "Droits sudo requis. Lancez le script avec sudo ou depuis un utilisateur ayant les droits sudo."
        exit 1
    fi
    
    log_success "Prérequis OK"
}

# Installation des dépendances système
install_system_deps() {
    log_info "Installation des dépendances système..."
    
    # Mise à jour des paquets
    sudo apt update
    sudo apt upgrade -y
    
    # Installation des paquets
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        wget \
        nano \
        htop \
        ufw \
        fail2ban \
        jq
    
    log_success "Dépendances système installées"
}

# Configuration du firewall
setup_firewall() {
    log_info "Configuration du firewall..."
    
    # Configuration UFW
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw allow 5000  # Port API pour les tests
    sudo ufw --force enable
    
    log_success "Firewall configuré"
}

# Création de l'utilisateur dédié
create_app_user() {
    log_info "Création de l'utilisateur utac-api..."
    
    # Vérifier si l'utilisateur existe déjà
    if id "utac-api" &>/dev/null; then
        log_warning "L'utilisateur utac-api existe déjà"
        return
    fi
    
    # Créer l'utilisateur
    sudo adduser --disabled-password --gecos "" utac-api
    sudo usermod -aG sudo utac-api
    
    # Créer le répertoire home si nécessaire
    sudo mkdir -p /home/utac-api
    sudo chown utac-api:utac-api /home/utac-api
    
    log_success "Utilisateur utac-api créé"
}

# Installation de l'application
install_application() {
    log_info "Installation de l'application UTAC-OTC..."
    
    # Devenir l'utilisateur utac-api
    sudo -u utac-api bash << 'EOF'
    
    # Aller dans le répertoire home
    cd /home/utac-api
    
    # Créer le répertoire de l'application
    mkdir -p utac-api
    cd utac-api
    
    # Créer l'environnement virtuel
    python3 -m venv venv
    source venv/bin/activate
    
    # Mettre à jour pip
    pip install --upgrade pip
    
    # Créer le fichier requirements.txt
    cat > requirements.txt << 'REQUIREMENTS'
# API UTAC-OTC - Dépendances Python
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
urllib3==2.0.7
gunicorn==21.2.0
lxml==4.9.3
REQUIREMENTS
    
    # Installer les dépendances
    pip install -r requirements.txt
    
    # Créer les répertoires nécessaires
    mkdir -p logs
    
EOF
    
    log_success "Application installée"
}

# Configuration Gunicorn
setup_gunicorn() {
    log_info "Configuration de Gunicorn..."
    
    sudo -u utac-api bash << 'EOF'
    cd /home/utac-api/utac-api
    
    # Créer la configuration Gunicorn
    cat > gunicorn.conf.py << 'GUNICORN_CONF'
# Configuration Gunicorn pour API UTAC-OTC
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False

# Logging
accesslog = "/home/utac-api/utac-api/logs/access.log"
errorlog = "/home/utac-api/utac-api/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Sécurité
user = "utac-api"
group = "utac-api"
GUNICORN_CONF
    
EOF
    
    log_success "Gunicorn configuré"
}

# Configuration du service systemd
setup_systemd_service() {
    log_info "Configuration du service systemd..."
    
    # Créer le fichier service
    sudo tee /etc/systemd/system/utac-api.service > /dev/null << 'SERVICE'
[Unit]
Description=API UTAC-OTC - Centres de contrôle technique français
After=network.target

[Service]
Type=exec
User=utac-api
Group=utac-api
WorkingDirectory=/home/utac-api/utac-api
Environment=PATH=/home/utac-api/utac-api/venv/bin
ExecStart=/home/utac-api/utac-api/venv/bin/gunicorn -c gunicorn.conf.py api:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/utac-api/utac-api
ProtectHome=true

[Install]
WantedBy=multi-user.target
SERVICE
    
    # Recharger systemd
    sudo systemctl daemon-reload
    sudo systemctl enable utac-api
    
    log_success "Service systemd configuré"
}

# Installation optionnelle de Nginx
install_nginx() {
    log_info "Voulez-vous installer Nginx comme proxy inverse ? (recommandé) (y/n)"
    read -r response
    
    if [[ ! $response =~ ^[Yy]$ ]]; then
        log_info "Installation de Nginx ignorée"
        return
    fi
    
    log_info "Installation et configuration de Nginx..."
    
    # Installation de Nginx
    sudo apt install -y nginx
    
    # Configuration du site
    sudo tee /etc/nginx/sites-available/utac-api > /dev/null << 'NGINX_CONF'
server {
    listen 80;
    server_name _;  # Accepte tous les noms de domaine

    # Logs
    access_log /var/log/nginx/utac-api.access.log;
    error_log /var/log/nginx/utac-api.error.log;

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts pour les longues requêtes (/all-centers)
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    # Sécurité
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
NGINX_CONF
    
    # Activer le site
    sudo ln -sf /etc/nginx/sites-available/utac-api /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Tester la configuration
    sudo nginx -t
    
    # Redémarrer Nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log_success "Nginx installé et configuré"
}

# Création du script de monitoring
create_monitoring_script() {
    log_info "Création du script de monitoring..."
    
    sudo -u utac-api bash << 'EOF'
    cd /home/utac-api/utac-api
    
    # Créer le script de monitoring
    cat > monitor.sh << 'MONITOR'
#!/bin/bash
# Script de monitoring API UTAC-OTC

echo "=== Statut API UTAC-OTC - $(date) ==="

# Test de l'API
echo "🔍 Test de l'API..."
if curl -s http://localhost:5000/health | jq '.' > /dev/null 2>&1; then
    echo "✅ API accessible"
else
    echo "❌ API non accessible"
fi

# Statut du service
echo "📊 Statut du service..."
systemctl is-active utac-api

# Utilisation des ressources
echo "💾 Utilisation mémoire..."
ps aux | grep gunicorn | grep -v grep | awk '{print "Process:", $2, "CPU:", $3"%", "RAM:", $4"%"}'

# Logs récents (si ils existent)
if [ -f "/home/utac-api/utac-api/logs/error.log" ]; then
    echo "📝 Logs récents..."
    tail -5 /home/utac-api/utac-api/logs/error.log
fi

echo "=== Fin du monitoring ==="
MONITOR
    
    chmod +x monitor.sh
EOF
    
    log_success "Script de monitoring créé"
}

# Affichage des instructions finales
show_final_instructions() {
    log_success "=== INSTALLATION TERMINÉE ==="
    echo ""
    log_info "Pour finaliser l'installation, vous devez :"
    echo "  1. Copier vos fichiers api.py et utac_scraper.py dans /home/utac-api/utac-api/"
    echo "  2. Démarrer le service : sudo systemctl start utac-api"
    echo "  3. Vérifier le statut : sudo systemctl status utac-api"
    echo ""
    log_info "Commandes utiles :"
    echo "  - Tester l'API : curl http://localhost:5000/health"
    echo "  - Monitoring : sudo -u utac-api /home/utac-api/utac-api/monitor.sh"
    echo "  - Logs : sudo journalctl -u utac-api -f"
    echo "  - Redémarrer : sudo systemctl restart utac-api"
    echo ""
    log_info "Structure des fichiers :"
    echo "  /home/utac-api/utac-api/"
    echo "  ├── api.py (À COPIER)"
    echo "  ├── utac_scraper.py (À COPIER)"
    echo "  ├── requirements.txt"
    echo "  ├── gunicorn.conf.py"
    echo "  ├── monitor.sh"
    echo "  ├── venv/"
    echo "  └── logs/"
    echo ""
    if systemctl is-enabled nginx >/dev/null 2>&1; then
        log_info "Nginx est installé. Votre API sera accessible via :"
        echo "  - http://votre-ip-serveur/"
        echo "  - http://votre-domaine.com/ (si configuré)"
    else
        log_info "API accessible directement sur :"
        echo "  - http://votre-ip-serveur:5000/"
    fi
}

# Fonction principale
main() {
    echo "=================================================="
    echo "  🚀 Installation API UTAC-OTC"
    echo "  Compatible Ubuntu 20.04/22.04"
    echo "=================================================="
    echo ""
    
    check_requirements
    install_system_deps
    setup_firewall
    create_app_user
    install_application
    setup_gunicorn
    setup_systemd_service
    install_nginx
    create_monitoring_script
    show_final_instructions
    
    log_success "Installation automatique terminée !"
}

# Lancer le script principal
main "$@"