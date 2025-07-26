#!/bin/bash

# =================================================================
# Script complet - Création repository GitHub + Push - CTAPIs
# Nécessite GitHub CLI (gh) installé et configuré
# =================================================================

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Création automatique du repository CTAPIs sur GitHub${NC}"
echo ""

# Vérifier GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) n'est pas installé${NC}"
    echo -e "${YELLOW}📦 Installez-le avec: brew install gh${NC}"
    echo -e "${YELLOW}🔑 Puis configurez-le avec: gh auth login${NC}"
    exit 1
fi

# Vérifier l'authentification
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI n'est pas authentifié${NC}"
    echo -e "${YELLOW}🔑 Configurez-le avec: gh auth login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI configuré${NC}"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "api.py" ] || [ ! -f "utac_scraper.py" ]; then
    echo -e "${RED}❌ Erreur: Lancez ce script depuis le répertoire contenant api.py${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Répertoire de travail:${NC} $(pwd)"
echo ""

# Créer le repository sur GitHub
echo -e "${BLUE}🏗️  Création du repository CTAPIs sur GitHub...${NC}"
gh repo create CTAPIs \
    --description "Collection d'APIs REST pour récupérer des informations depuis différents sites officiels français" \
    --public \
    --clone=false \
    --add-readme=false

echo -e "${GREEN}✅ Repository CTAPIs créé sur GitHub${NC}"

# Initialiser Git si nécessaire
if [ ! -d ".git" ]; then
    echo -e "${BLUE}🔧 Initialisation de Git...${NC}"
    git init
else
    echo -e "${GREEN}✅ Repository Git déjà initialisé${NC}"
fi

# Configurer Git si nécessaire
if ! git config user.name > /dev/null 2>&1; then
    echo -e "${BLUE}👤 Configuration Git...${NC}"
    # Récupérer les infos depuis GitHub CLI
    GH_USER=$(gh api user --jq .name 2>/dev/null || echo "")
    GH_EMAIL=$(gh api user --jq .email 2>/dev/null || echo "")
    
    if [ -n "$GH_USER" ] && [ -n "$GH_EMAIL" ]; then
        git config user.name "$GH_USER"
        git config user.email "$GH_EMAIL"
        echo -e "${GREEN}✅ Git configuré avec les infos GitHub${NC}"
    else
        read -p "Votre nom pour Git: " git_name
        read -p "Votre email pour Git: " git_email
        git config user.name "$git_name"
        git config user.email "$git_email"
        echo -e "${GREEN}✅ Git configuré${NC}"
    fi
fi

# Ajouter tous les fichiers
echo -e "${BLUE}📦 Ajout des fichiers...${NC}"
git add .

# Commit
echo -e "${BLUE}💾 Création du commit initial...${NC}"
git commit -m "🚀 Initial commit - CTAPIs avec API UTAC-OTC

✨ Fonctionnalités principales:
- API UTAC-OTC complète pour centres de contrôle technique français
- Recherche par agrément, département et récupération complète (~6800 centres)
- Pagination automatique et extraction de colonnes cachées
- Documentation interactive avec Redoc (docs-inline.html)
- Spécification OpenAPI complète (openapi.yaml)

🛠️ Infrastructure et déploiement:
- Guide d'installation VPS détaillé (installation-guide.html)
- Script d'installation automatique (install.sh)
- Script de déploiement/mise à jour (deploy.sh)
- Configuration production prête (Gunicorn, Nginx, systemd)
- Fichiers de configuration optimisés dans configs/

📁 Structure préparée pour futures APIs:
- Architecture modulaire pour ajouter de nouvelles APIs de scraping
- Conventions et patterns établis
- Documentation et exemples prêts

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Ajouter le remote
echo -e "${BLUE}🔗 Configuration du remote GitHub...${NC}"
git remote add origin https://github.com/simplauto/CTAPIs.git

# Pousser vers GitHub
echo -e "${BLUE}🚀 Push vers GitHub...${NC}"
git branch -M main
git push -u origin main

# Ajouter des topics au repository
echo -e "${BLUE}🏷️  Ajout de topics au repository...${NC}"
gh repo edit --add-topic api,scraping,python,flask,rest-api,utac-otc,technical-inspection,french-data

echo ""
echo -e "${GREEN}🎉 SUCCESS! 🎉${NC}"
echo -e "${GREEN}Votre projet CTAPIs est maintenant sur GitHub:${NC}"
echo -e "${BLUE}👉 https://github.com/simplauto/CTAPIs${NC}"
echo ""

# Afficher le lien vers la documentation
echo -e "${BLUE}📖 Liens utiles:${NC}"
echo "• Repository: https://github.com/simplauto/CTAPIs"
echo "• Documentation: https://github.com/simplauto/CTAPIs/blob/main/docs-inline.html"
echo "• Guide installation: https://github.com/simplauto/CTAPIs/blob/main/installation-guide.html"
echo "• Script d'installation: https://raw.githubusercontent.com/simplauto/CTAPIs/main/install.sh"
echo ""
echo -e "${GREEN}🚀 Votre projet CTAPIs est prêt pour de nouvelles APIs !${NC}"