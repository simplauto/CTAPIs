# 🚗 CTAPIs - Collection d'APIs de Scraping

Collection d'APIs REST pour récupérer des informations depuis différents sites officiels français.

## 📂 APIs Disponibles

### 🚗 API UTAC-OTC - Centres de contrôle technique français
API REST pour récupérer les informations des centres de contrôle technique français à partir des données officielles UTAC-OTC.

#### 📋 Fonctionnalités UTAC-OTC

- **Recherche par numéro d'agrément** : Informations détaillées d'un centre spécifique
- **Recherche par département** : Tous les centres d'un département (pagination automatique)
- **Récupération complète** : Tous les centres de France (~6800 centres)
- **API REST** avec réponses JSON
- **Documentation interactive** avec Redoc
- **Support CORS** pour les applications web

#### 🔗 Endpoints UTAC-OTC

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérification de l'état de l'API |
| `/agreement/{numero}` | GET | Recherche par numéro d'agrément |
| `/agreement` | POST | Recherche par numéro d'agrément (JSON) |
| `/department/{code}` | GET | Tous les centres d'un département |
| `/department` | POST | Recherche par département (JSON) |
| `/all-centers` | GET | Tous les centres de France ⚠️ (6-8 min) |

#### 📖 Documentation UTAC-OTC

- **Documentation interactive** : Ouvrez `docs-inline.html` dans votre navigateur
- **Spécification OpenAPI** : `openapi.yaml`
- **Guide d'installation VPS** : `installation-guide.html`

---

## 🚀 Prochaines APIs en développement

- 📋 **API Autre Site** - Description à venir
- 🏢 **API Autre Service** - Description à venir

*Suggestions d'APIs ? Ouvrez une issue !*

---

## ⚡ Installation rapide (API UTAC-OTC)

### Prérequis
- Python 3.8+
- pip

### Installation locale
```bash
# 1. Cloner le repository
git clone https://github.com/simplauto/CTAPIs.git
cd CTAPIs

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'API
python api.py
```

L'API sera accessible sur : http://localhost:5000

## 🌐 Installation sur VPS (Production)

### Installation automatique
```bash
# Télécharger et lancer le script d'installation
curl -O https://raw.githubusercontent.com/simplauto/CTAPIs/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

### Installation manuelle
Consultez le [Guide d'installation détaillé](installation-guide.html) pour une installation pas-à-pas sur VPS Ubuntu.

## 📋 Endpoints

### GET `/`
Documentation de l'API avec exemples d'utilisation.

### GET `/health`
Vérification de l'état de l'API.

**Réponse :**
```json
{
    "status": "healthy",
    "service": "UTAC-OTC API",
    "version": "1.0.0"
}
```

### GET `/agreement/<agreement_number>`
Recherche par numéro d'agrément via URL.

**Exemple :**
```bash
curl "http://localhost:8000/agreement/S044C203"
```

### GET `/department/<department_code>`
Recherche tous les centres d'un département via URL. Gère automatiquement la pagination pour récupérer tous les centres.

**Exemple :**
```bash
curl "http://localhost:8000/department/04"
```

**Réponse :**
```json
{
    "success": true,
    "data": {
        "department_code": "04",
        "total_centers": 25,
        "centers": [
            {
                "raison_sociale": "BA CONTROLE",
                "agreement_number": "S004S062",
                "enseigne": "BA CONTROLE",
                "adresse": "3 AVENUE EMILE AUBERT",
                "ville": "BARCELONNETTE",
                "code_postal": "04400",
                "telephone": "04 92 81 15 89",
                "option": "",
                "site_internet": ""
            }
        ]
    }
}
```

### GET `/agreement/<agreement_number>`
Recherche par numéro d'agrément via URL.

**Exemple :**
```bash
curl "http://localhost:8000/agreement/S044C203"
```

**Réponse :**
```json
{
    "success": true,
    "data": {
        "agreement_number": "S044C203",
        "raison_sociale": "CONTROLE TECHNIQUE SAINT SEB",
        "enseigne": "AUTO SECURITE",
        "adresse": "329 ROUTE DE CLISSON ZAC DES GRIPOTS",
        "ville": "ST SEBASTIEN SUR LOIRE",
        "code_postal": "44230",
        "telephone": "02 40 80 06 00",
        "option": "GAZ*",
        "site_internet": "",
        "url": "Page de résultats"
    }
}
```

### POST `/agreement`
Recherche par numéro d'agrément via JSON body.

**Body JSON :**
```json
{
    "agreement_number": "S044C203"
}
```

**Exemple :**
```bash
curl -X POST http://localhost:8000/agreement \
  -H "Content-Type: application/json" \
  -d '{"agreement_number": "S044C203"}'
```

### POST `/department`
Recherche tous les centres d'un département via JSON body.

**Body JSON :**
```json
{
    "department_code": "04"
}
```

**Exemple :**
```bash
curl -X POST http://localhost:8000/department \
  -H "Content-Type: application/json" \
  -d '{"department_code": "04"}'
```

## 🔧 Utilisation du Scraper en Standalone

Vous pouvez aussi utiliser le scraper directement :

```bash
# Test avec un numéro d'agrément
source venv/bin/activate
python test_agreement.py S044C203

# Ou directement en Python
python3 -c "
from utac_scraper import UTACScraper
scraper = UTACScraper()
result = scraper.search_by_agreement_number('S044C203')
print(result)
"
```

## 📄 Structure des Données Retournées

### Recherche par agrément
```json
{
    "success": true,
    "data": {
        "agreement_number": "Numéro d'agrément recherché",
        "raison_sociale": "Nom officiel du centre",
        "enseigne": "Nom de l'enseigne commerciale",
        "adresse": "Adresse complète",
        "ville": "Nom de la ville",
        "code_postal": "Code postal",
        "telephone": "Numéro de téléphone",
        "option": "Options disponibles (GAZ, etc.)",
        "site_internet": "Site web du centre",
        "url": "Source des données"
    }
}
```

### Recherche par département
```json
{
    "success": true,
    "data": {
        "department_code": "Code du département",
        "total_centers": "Nombre total de centres",
        "centers": [
            {
                "raison_sociale": "Nom officiel du centre",
                "agreement_number": "Numéro d'agrément",
                "enseigne": "Nom de l'enseigne commerciale",
                "adresse": "Adresse complète",
                "ville": "Nom de la ville",
        "code_postal": "Code postal",
                "telephone": "Numéro de téléphone",
                "option": "Options disponibles (GAZ, etc.)",
                "site_internet": "Site web du centre"
            }
        ]
    }
}
```

## ⚠️ Gestion d'Erreurs

### Numéro d'agrément non trouvé (404)
```json
{
    "success": false,
    "error": "Lien détail non trouvé",
    "agreement_number": "INVALID123"
}
```

### Paramètre manquant (400)
```json
{
    "success": false,
    "error": "Paramètre agreement_number requis dans le body JSON"
}
```

### Erreur serveur (500)
```json
{
    "success": false,
    "error": "Erreur interne du serveur"
}
```

## 🧪 Tests

Tests avec curl :

```bash
# Health check
curl http://localhost:8000/health

# Recherche valide
curl "http://localhost:8000/agreement/S044C203"

# Recherche avec POST
curl -X POST http://localhost:8000/agreement \
  -H "Content-Type: application/json" \
  -d '{"agreement_number": "S044C203"}'

# Test avec numéro invalide
curl "http://localhost:8000/agreement/INVALID123"

# Test recherche département
curl "http://localhost:8000/department/04"

# Test recherche avec POST
curl -X POST http://localhost:8000/department \
  -H "Content-Type: application/json" \
  -d '{"department_code": "04"}'
```

## 🗺️ Codes Départements Supportés

- **Départements métropolitains** : 01 à 95 (format: "01", "02", ..., "95")
- **DOM-TOM** : 971 à 989 (format: "971", "972", etc.)

**Important** : Pour les départements 1 à 9, utilisez le format avec zéro initial ("01", "02", etc.)

## 📁 Fichiers du Projet

- `api.py` - API Flask principale
- `utac_scraper.py` - Scraper UTAC-OTC
- `test_agreement.py` - Script de test standalone
- `README.md` - Documentation

## 🚨 Notes Importantes

- Cette API scrappe le site UTAC-OTC et dépend de sa structure
- Respectez les conditions d'utilisation du site UTAC-OTC
- L'API désactive la vérification SSL pour contourner les problèmes de certificats
- Utilisez un serveur WSGI en production (pas le serveur de développement Flask)
- **Recherche par département** : Gère automatiquement la pagination pour récupérer TOUS les centres
- **Colonnes cachées** : Récupère toutes les informations, y compris celles masquées dans l'interface web