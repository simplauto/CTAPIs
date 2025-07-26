#!/bin/bash

# =================================================================
# Script de push automatique vers GitHub - CTAPIs
# Utilisez ce script après avoir créé le repository sur GitHub
# =================================================================

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Push automatique vers GitHub - CTAPIs${NC}"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "api.py" ] || [ ! -f "utac_scraper.py" ]; then
    echo -e "${RED}❌ Erreur: Lancez ce script depuis le répertoire contenant api.py${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Répertoire de travail:${NC} $(pwd)"
echo ""

# Initialiser Git si nécessaire
if [ ! -d ".git" ]; then
    echo -e "${BLUE}🔧 Initialisation de Git...${NC}"
    git init
    echo -e "${GREEN}✅ Git initialisé${NC}"
else
    echo -e "${GREEN}✅ Repository Git déjà initialisé${NC}"
fi

# Configurer Git si nécessaire
if ! git config user.name > /dev/null 2>&1; then
    echo -e "${BLUE}👤 Configuration Git...${NC}"
    read -p "Votre nom pour Git: " git_name
    read -p "Votre email pour Git: " git_email
    git config user.name "$git_name"
    git config user.email "$git_email"
    echo -e "${GREEN}✅ Git configuré${NC}"
fi

# Ajouter tous les fichiers
echo -e "${BLUE}📦 Ajout des fichiers...${NC}"
git add .

# Vérifier les fichiers ajoutés
echo -e "${BLUE}📋 Fichiers qui seront commités:${NC}"
git status --porcelain

echo ""
read -p "Continuer avec le commit ? (y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Annulé"
    exit 0
fi

# Commit
echo -e "${BLUE}💾 Création du commit...${NC}"
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

echo -e "${GREEN}✅ Commit créé${NC}"

# Ajouter le remote si nécessaire
if ! git remote get-url origin > /dev/null 2>&1; then
    echo -e "${BLUE}🔗 Ajout du remote GitHub...${NC}"
    git remote add origin https://github.com/simplauto/CTAPIs.git
    echo -e "${GREEN}✅ Remote ajouté${NC}"
else
    echo -e "${GREEN}✅ Remote déjà configuré${NC}"
fi

# Renommer la branche en main
echo -e "${BLUE}🌿 Configuration de la branche main...${NC}"
git branch -M main

# Push vers GitHub
echo -e "${BLUE}🚀 Push vers GitHub...${NC}"
git push -u origin main

echo ""
echo -e "${GREEN}🎉 SUCCESS! 🎉${NC}"
echo -e "${GREEN}Votre projet CTAPIs est maintenant sur GitHub:${NC}"
echo -e "${BLUE}👉 https://github.com/simplauto/CTAPIs${NC}"
echo ""
echo -e "${BLUE}📖 Prochaines étapes:${NC}"
echo "1. Vérifiez que tout est bien sur GitHub"
echo "2. Ajoutez une description au repository si nécessaire"
echo "3. Configurez les GitHub Pages pour la documentation (optionnel)"
echo "4. Ajoutez des topics/tags au repository (api, scraping, python, etc.)"
echo ""
echo -e "${GREEN}🚀 Votre projet CTAPIs est prêt pour de nouvelles APIs !${NC}"