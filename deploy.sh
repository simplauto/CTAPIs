#!/bin/bash

# =================================================================
# Script de déploiement rapide - API UTAC-OTC
# Pour mettre à jour une installation existante
# =================================================================

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
APP_DIR="/home/utac-api/utac-api"
SERVICE_NAME="utac-api"
BACKUP_DIR="/home/utac-api/backups"

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

# Vérification que l'installation existe
check_installation() {
    log_info "Vérification de l'installation existante..."
    
    if [ ! -d "$APP_DIR" ]; then
        log_error "Installation non trouvée dans $APP_DIR"
        log_error "Lancez d'abord install.sh pour installer l'application"
        exit 1
    fi
    
    if ! systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
        log_error "Service $SERVICE_NAME non trouvé"
        log_error "Lancez d'abord install.sh pour configurer le service"
        exit 1
    fi
    
    log_success "Installation existante trouvée"
}

# Création d'une sauvegarde
create_backup() {
    log_info "Création d'une sauvegarde..."
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/utac-api_backup_$TIMESTAMP.tar.gz"
    
    # Créer le répertoire de backup
    sudo -u utac-api mkdir -p "$BACKUP_DIR"
    
    # Arrêter le service
    sudo systemctl stop "$SERVICE_NAME"
    
    # Créer la sauvegarde
    sudo -u utac-api tar -czf "$BACKUP_FILE" \
        -C "$(dirname $APP_DIR)" \
        "$(basename $APP_DIR)" \
        --exclude='*/venv/*' \
        --exclude='*/logs/*' \
        --exclude='*/__pycache__/*'
    
    log_success "Sauvegarde créée : $BACKUP_FILE"
}

# Mise à jour des fichiers
update_files() {
    log_info "Mise à jour des fichiers..."
    
    # Vérifier que les fichiers sources existent
    CURRENT_DIR=$(pwd)
    
    if [ ! -f "$CURRENT_DIR/api.py" ]; then
        log_error "Fichier api.py non trouvé dans le répertoire courant"
        exit 1
    fi
    
    if [ ! -f "$CURRENT_DIR/utac_scraper.py" ]; then
        log_error "Fichier utac_scraper.py non trouvé dans le répertoire courant"
        exit 1
    fi
    
    # Copier les nouveaux fichiers
    sudo -u utac-api cp "$CURRENT_DIR/api.py" "$APP_DIR/"
    sudo -u utac-api cp "$CURRENT_DIR/utac_scraper.py" "$APP_DIR/"
    
    # Mettre à jour requirements.txt si présent
    if [ -f "$CURRENT_DIR/requirements.txt" ]; then
        sudo -u utac-api cp "$CURRENT_DIR/requirements.txt" "$APP_DIR/"
        log_info "requirements.txt mis à jour"
    fi
    
    # Mettre à jour la configuration Gunicorn si présente
    if [ -f "$CURRENT_DIR/configs/gunicorn.conf.py" ]; then
        sudo -u utac-api cp "$CURRENT_DIR/configs/gunicorn.conf.py" "$APP_DIR/"
        log_info "gunicorn.conf.py mis à jour"
    fi
    
    log_success "Fichiers mis à jour"
}

# Mise à jour des dépendances
update_dependencies() {
    log_info "Mise à jour des dépendances..."
    
    sudo -u utac-api bash << 'EOF'
cd /home/utac-api/utac-api
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade
EOF
    
    log_success "Dépendances mises à jour"
}

# Test de l'application
test_application() {
    log_info "Test de l'application..."
    
    # Démarrer le service
    sudo systemctl start "$SERVICE_NAME"
    
    # Attendre que le service démarre
    sleep 5
    
    # Tester l'API
    if curl -s -f http://localhost:5000/health > /dev/null; then
        log_success "API fonctionne correctement"
    else
        log_error "API ne répond pas"
        log_info "Vérification des logs..."
        sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20
        exit 1
    fi
}

# Nettoyage des anciennes sauvegardes
cleanup_backups() {
    log_info "Nettoyage des anciennes sauvegardes..."
    
    # Garder seulement les 5 dernières sauvegardes
    sudo -u utac-api bash << 'EOF'
cd /home/utac-api/backups 2>/dev/null || exit 0
ls -t utac-api_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f
EOF
    
    log_success "Anciennes sauvegardes supprimées"
}

# Affichage du statut final
show_status() {
    log_info "=== STATUT FINAL ==="
    
    # Statut du service
    echo "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    
    echo ""
    
    # Test rapide de l'API
    echo "API Health Check:"
    curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || echo "Erreur lors du test"
    
    echo ""
    log_info "Commandes utiles :"
    echo "  - Logs en temps réel : sudo journalctl -u $SERVICE_NAME -f"
    echo "  - Redémarrer : sudo systemctl restart $SERVICE_NAME"
    echo "  - Monitoring : sudo -u utac-api $APP_DIR/monitor.sh"
    echo "  - Restaurer sauvegarde : tar -xzf /home/utac-api/backups/utac-api_backup_TIMESTAMP.tar.gz -C /"
}

# Fonction principale
main() {
    echo "=================================================="
    echo "  🔄 Déploiement API UTAC-OTC"
    echo "  Mise à jour d'une installation existante"
    echo "=================================================="
    echo ""
    
    check_installation
    create_backup
    update_files
    update_dependencies
    test_application
    cleanup_backups
    show_status
    
    log_success "Déploiement terminé avec succès !"
}

# Options de ligne de commande
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Afficher cette aide"
        echo "  --no-backup    Ne pas créer de sauvegarde"
        echo "  --force        Forcer la mise à jour même en cas d'erreur"
        echo ""
        echo "Ce script met à jour une installation existante de l'API UTAC-OTC."
        echo "Il faut lancer ce script depuis le répertoire contenant api.py et utac_scraper.py"
        exit 0
        ;;
    --no-backup)
        log_warning "Mode sans sauvegarde activé"
        create_backup() { log_info "Sauvegarde ignorée"; }
        shift
        ;;
    --force)
        log_warning "Mode forcé activé"
        set +e  # Continuer en cas d'erreur
        shift
        ;;
esac

# Lancer le déploiement
main "$@"