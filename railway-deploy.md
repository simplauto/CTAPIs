# 🚂 Déploiement Railway - CTAPIs

Guide pour déployer l'API UTAC-OTC sur Railway.

## 🎯 Prérequis

- ✅ Compte Railway (https://railway.app)
- ✅ Repository GitHub CTAPIs configuré
- ✅ Fichiers Railway dans le repository

## 📁 Fichiers Railway

Le repository contient maintenant :

- **`Procfile`** - Commande de démarrage pour Railway
- **`railway.json`** - Configuration Railway avec variables d'environnement
- **`gunicorn-railway.conf.py`** - Configuration Gunicorn optimisée Railway
- **`api.py`** - Adapté pour port dynamique Railway

## 🚀 Déploiement automatique

### Étape 1 : Connecter GitHub

1. Allez sur https://railway.app
2. Connectez-vous avec GitHub
3. Cliquez **"New Project"**
4. Sélectionnez **"Deploy from GitHub repo"**
5. Choisissez le repository **`simplauto/CTAPIs`**

### Étape 2 : Configuration automatique

Railway détectera automatiquement :
- ✅ **Python** via `requirements.txt`
- ✅ **Commande de démarrage** via `Procfile`
- ✅ **Configuration** via `railway.json`
- ✅ **Health check** sur `/health`

### Étape 3 : Variables d'environnement

Railway configurera automatiquement :
- `PORT` - Port dynamique Railway
- `FLASK_ENV=production` 
- `LOG_LEVEL=info`
- `WEB_CONCURRENCY=2`
- `PYTHONUNBUFFERED=1`

## 🔗 Après déploiement

### URLs accessibles

Votre API sera disponible sur : `https://votre-app.railway.app`

**Endpoints :**
- `GET /` - Documentation de l'API
- `GET /health` - Health check
- `GET /agreement/{numero}` - Recherche par agrément
- `GET /department/{code}` - Recherche par département
- `GET /all-centers` - Tous les centres (6-8 min)

### Tests de base

```bash
# Remplacez YOUR-APP par le nom de votre app Railway
export RAILWAY_URL="https://YOUR-APP.railway.app"

# Test health check
curl $RAILWAY_URL/health

# Test recherche par agrément
curl "$RAILWAY_URL/agreement/S044C203"

# Test recherche par département
curl "$RAILWAY_URL/department/04"
```

## 📊 Monitoring Railway

### Logs en temps réel
- Allez dans Railway Dashboard
- Sélectionnez votre projet CTAPIs
- Onglet **"Deployments"** > **"View Logs"**

### Métriques
- **CPU** : Surveillez l'utilisation
- **Mémoire** : ~200-400 MB typique
- **Réseau** : Dépend de l'usage

### Health check
Railway vérifie automatiquement `/health` toutes les 30 secondes.

## ⚙️ Configuration avancée

### Scaling
```json
{
  "environments": {
    "production": {
      "variables": {
        "WEB_CONCURRENCY": "4"  // Plus de workers
      }
    }
  }
}
```

### Custom domain
Dans Railway Dashboard :
1. **Settings** > **Domains**
2. **Add Custom Domain**
3. Configurez votre DNS

### Variables d'environnement custom
Dans Railway Dashboard :
1. **Variables** 
2. **Add Variable**
3. Redéployez automatiquement

## 🐛 Debugging

### Erreurs communes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `No start command` | Pas de Procfile | ✅ Ajouté |
| `Port binding failed` | Port hardcodé | ✅ Corrigé |
| `Module not found` | Dépendance manquante | Vérifier `requirements.txt` |
| `Health check failed` | `/health` inaccessible | Vérifier l'app Flask |

### Logs utiles

```bash
# Via Railway CLI (optionnel)
railway logs

# Ou dans Dashboard > Deployments > View Logs
```

### Test local Railway-like

```bash
# Simuler l'environnement Railway localement
export PORT=8000
export FLASK_ENV=production
export WEB_CONCURRENCY=2

# Lancer avec Gunicorn comme Railway
gunicorn -c gunicorn-railway.conf.py api:app
```

## 🔄 Mise à jour

Pour mettre à jour l'API :

1. **Modifiez le code** localement
2. **Commit et push** vers GitHub
3. **Railway redéploie automatiquement**

```bash
git add .
git commit -m "🚀 Update API"
git push origin main
# Railway détecte et redéploie automatiquement
```

## 💡 Optimisations Railway

### Performance
- **Workers** : 2-4 selon le trafic
- **Timeout** : 120s pour `/all-centers`
- **Keep-alive** : Activé

### Sécurité
- **HTTPS** : Automatique Railway
- **CORS** : Configuré pour Railway domains
- **Logs** : Pas de données sensibles

### Coûts
- **Plan gratuit** : 500h/mois, $5 après
- **Plan Pro** : $20/mois, ressources dédiées
- **Monitoring** : Inclus

## 🎉 Success !

Votre API UTAC-OTC est maintenant déployée sur Railway ! 

**Liens utiles :**
- 🚂 Railway Dashboard : https://railway.app/dashboard
- 📖 Railway Docs : https://docs.railway.app
- 🐛 Railway Discord : https://discord.gg/railway

**Prochaines étapes :**
- Testez tous les endpoints
- Configurez un domaine custom (optionnel)
- Surveillez les performances
- Ajoutez de nouvelles APIs au projet CTAPIs !