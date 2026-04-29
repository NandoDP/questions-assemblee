# 🚀 Guide de Déploiement sur Render

Ce guide vous accompagne pas à pas pour déployer l'architecture complète sur Render.

## 📋 Prérequis

- [x] Compte GitHub avec le repo `questions-assemblee`
- [x] Compte [Render.com](https://render.com) (gratuit)
- [x] Base de données PostgreSQL initialisée avec `db-init.sql`
- [x] Modèle CamemBERT uploadé sur HuggingFace (optionnel)

---

## 🏗️ Architecture du Déploiement

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                  (questions-assemblee)                       │
└───────────┬──────────────────────────────┬──────────────────┘
            │                              │
            │ GitHub Actions (ETL Cron)    │
            │ ↓ Tous les jours à 2h        │
            │                              │
            ↓                              ↓
┌───────────────────────┐      ┌──────────────────────────┐
│   PostgreSQL (Render) │◄────►│  Superset (Web Service)  │
│   Free Tier (256 MB)  │      │  Dashboard BI            │
└───────────────────────┘      └──────────┬───────────────┘
                                          │ iframe embed
                                          ↓
                               ┌──────────────────────────┐
                               │  Flask App (Web Service) │
                               │  Dashboard Public        │
                               └──────────────────────────┘
```

---

## 🎯 Étape 1 : Créer la Base de Données PostgreSQL

### 1.1 Depuis le Dashboard Render

1. Connexion à [dashboard.render.com](https://dashboard.render.com)
2. Cliquer sur **New +** → **PostgreSQL**
3. Remplir les informations :
   - **Name** : `questions-assemblee-db`
   - **Database** : `questions_assemblee`
   - **User** : `questions_user`
   - **Region** : Frankfurt (ou Oregon)
   - **Plan** : Free

4. Cliquer sur **Create Database**

5. ⏳ Attendre 2-3 minutes que la DB soit provisionnée

### 1.2 Récupérer les informations de connexion

Une fois la DB créée :

1. Aller dans l'onglet **Info**
2. Copier **Internal Database URL** (format : `postgresql://user:pass@host/db`)
3. Copier **External Database URL** (pour connexion locale)

### 1.3 Initialiser la base de données

**Option A : Via psql (recommandé)**

```bash
# Installer psql si nécessaire
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: apt-get install postgresql-client

# Se connecter à la DB Render
psql "postgresql://user:pass@host/db"

# Exécuter le script d'initialisation
\i db-init.sql

# Vérifier que les tables sont créées
\dt

# Quitter
\q
```

**Option B : Via DBeaver / pgAdmin**

1. Ouvrir DBeaver ou pgAdmin
2. Créer une nouvelle connexion PostgreSQL
3. Coller l'External Database URL
4. Exécuter le contenu de `db-init.sql`

---

## 🎯 Étape 2 : Déployer Apache Superset

### 2.1 Créer le Web Service

1. Dashboard Render → **New +** → **Web Service**
2. Connecter votre repo GitHub `NandoDP/questions-assemblee`
3. Remplir les informations :
   - **Name** : `questions-assemblee-superset`
   - **Region** : Frankfurt
   - **Branch** : `main`
   - **Runtime** : Docker
   - **Dockerfile Path** : `Dockerfile.superset`
   - **Plan** : Free

### 2.2 Configurer les Variables d'Environnement

Dans la section **Environment** :

| Variable | Valeur |
|----------|--------|
| `DATABASE_URL` | Coller l'Internal Database URL de l'étape 1.2 |
| `SUPERSET_SECRET_KEY` | Générer avec : `openssl rand -base64 42` |
| `SUPERSET_JWT_SECRET` | Générer avec : `openssl rand -base64 42` |
| `SUPERSET_ADMIN_PASSWORD` | Choisir un mot de passe fort |
| `PORT` | `8088` (automatique sur Render) |

### 2.3 Configurer le Health Check

- **Health Check Path** : `/health`

### 2.4 Déployer

1. Cliquer sur **Create Web Service**
2. ⏳ Attendre 5-10 minutes pour le premier déploiement
3. Suivre les logs en temps réel

### 2.5 Accéder à Superset

1. Une fois déployé, cliquer sur l'URL fournie (ex: `https://questions-assemblee-superset.onrender.com`)
2. Se connecter avec :
   - **Username** : `admin`
   - **Password** : La valeur de `SUPERSET_ADMIN_PASSWORD`

### 2.6 Configurer Superset

#### A. Ajouter la source de données

1. Dans Superset : **Settings** → **Database Connections** → **+ Database**
2. Sélectionner **PostgreSQL**
3. Remplir :
   - **Display Name** : `Questions Assemblée`
   - **SQLAlchemy URI** : L'Internal Database URL (remplacer `postgres://` par `postgresql://`)
   - Cocher **Allow DML** (décoché pour sécurité)
   - Cocher **Allow file uploads**
4. Cliquer sur **Test Connection**
5. **Save**

#### B. Créer un Dataset

1. **Data** → **Datasets** → **+ Dataset**
2. Sélectionner la table `questions` (ou la vue `vue_questions_complete`)
3. **Save**

#### C. Créer un Dashboard

1. **Dashboards** → **+ Dashboard**
2. Nommer : `Questions Parlementaires`
3. Ajouter des graphiques :
   - **Questions par ministère** (Bar Chart)
   - **Évolution temporelle** (Line Chart)
   - **Répartition thématique** (Pie Chart)
   - **Top députés** (Table)
   - **Carte géographique** (Map)

#### D. Rendre le Dashboard Public

1. Ouvrir le dashboard créé
2. Cliquer sur **...** → **Share** → **Dashboard permalink**
3. Activer **Public**
4. Copier l'URL (format : `/superset/dashboard/1/?standalone=true`)
5. Noter le **Dashboard ID** (ex: `1`)

---

## 🎯 Étape 3 : Déployer l'Application Flask

### 3.1 Créer le Web Service

1. Dashboard Render → **New +** → **Web Service**
2. Connecter le même repo GitHub
3. Remplir :
   - **Name** : `questions-assemblee-dashboard`
   - **Region** : Frankfurt
   - **Branch** : `main`
   - **Runtime** : Docker
   - **Dockerfile Path** : `Dockerfile.flask`
   - **Plan** : Free

### 3.2 Configurer les Variables d'Environnement

| Variable | Valeur |
|----------|--------|
| `SUPERSET_URL` | `https://questions-assemblee-superset.onrender.com` |
| `DASHBOARD_ID` | L'ID du dashboard (ex: `1`) |
| `FLASK_SECRET_KEY` | Générer avec : `openssl rand -base64 32` |
| `PORT` | `5000` (automatique sur Render) |

### 3.3 Configurer le Health Check

- **Health Check Path** : `/health`

### 3.4 Déployer

1. Cliquer sur **Create Web Service**
2. ⏳ Attendre 3-5 minutes
3. Accéder à l'URL fournie : **C'est votre dashboard public !** 🎉

---

## 🎯 Étape 4 : Configurer GitHub Actions (ETL)

### 4.1 Ajouter les Secrets GitHub

1. Aller sur GitHub : `NandoDP/questions-assemblee`
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquer sur **New repository secret**

Ajouter ces secrets :

| Secret | Valeur |
|--------|--------|
| `DATABASE_URL` | Internal Database URL de Render |
| `API_TOKEN` | Token de l'API Assemblée Nationale |
| `GHCR_TOKEN` | Personal Access Token GitHub (si Docker images) |

### 4.2 Tester le Workflow ETL Manuellement

1. GitHub → **Actions** → **Scheduled ETL Pipeline**
2. Cliquer sur **Run workflow** → **Run workflow**
3. Suivre l'exécution dans les logs
4. ✅ Vérifier que des données sont ajoutées dans la DB

### 4.3 Planification Automatique

Le workflow s'exécutera automatiquement tous les jours à 2h UTC grâce à :

```yaml
on:
  schedule:
    - cron: '0 2 * * *'
```

---

## 🎯 Étape 5 : Vérifications et Tests

### 5.1 Checklist de Déploiement

- [ ] PostgreSQL déployé et initialisé
- [ ] Superset accessible et configuré
- [ ] Dashboard créé et rendu public
- [ ] Flask App affiche le dashboard
- [ ] GitHub Actions exécute l'ETL sans erreur
- [ ] Données apparaissent dans Superset

### 5.2 Tester les Services

**PostgreSQL** :
```bash
psql "postgresql://user:pass@host/db" -c "SELECT COUNT(*) FROM questions;"
```

**Superset** :
```bash
curl https://questions-assemblee-superset.onrender.com/health
```

**Flask Dashboard** :
```bash
curl https://questions-assemblee-dashboard.onrender.com/health
```

**ETL GitHub Actions** :
Vérifier le dernier run dans l'onglet Actions

---

## 🔧 Configuration Avancée

### Option A : Ajouter Redis (pour cache Superset)

1. Render → **New +** → **Redis**
2. Plan : Free (25 MB)
3. Copier le **Internal Redis URL**
4. Ajouter à Superset :
   ```env
   REDIS_URL=redis://...
   ```
5. Mettre à jour `superset_config.py` :
   ```python
   CACHE_CONFIG = {
       'CACHE_TYPE': 'redis',
       'CACHE_REDIS_URL': os.getenv('REDIS_URL')
   }
   ```

### Option B : Utiliser Render Disk Storage

Pour stocker le modèle ML (422 MB) :

1. Render → **New +** → **Disk**
2. Taille : 10 GB (gratuit)
3. Monter sur `/app/models` dans le service Superset
4. Uploader le modèle via SSH :
   ```bash
   scp models/camembert_model/model.safetensors render:/app/models/
   ```

---

## 📊 Monitoring et Maintenance

### Logs

Accéder aux logs de chaque service via le dashboard Render :
- Superset : **Logs** tab
- Flask : **Logs** tab
- GitHub Actions : Onglet **Actions** sur GitHub

### Limites du Plan Free

| Service | Limite | Upgrade |
|---------|--------|---------|
| PostgreSQL | 256 MB | $7/mois → 1 GB |
| Web Service | 750h/mois | $7/mois → Illimité |
| Build Minutes | 500 min/mois | $7/mois → 1000 min |

### Redémarrages Automatiques

Sur le plan Free, les services s'endorment après 15 min d'inactivité.
Premier accès après inactivité : ⏳ 30-60 secondes de délai.

**Solution** : Upgrade au plan payant ($7/mois) pour garder actif 24/7.

---

## 🎉 Résultat Final

Vous avez maintenant :

✅ **Dashboard public** accessible via URL Render  
✅ **ETL automatisé** qui s'exécute chaque jour  
✅ **Base de données PostgreSQL** avec données structurées  
✅ **Pipeline ML** pour classification des questions  
✅ **Infrastructure as Code** avec `render.yaml`

### URLs d'exemple

- Dashboard Public : `https://questions-assemblee-dashboard.onrender.com`
- Superset Admin : `https://questions-assemblee-superset.onrender.com`
- GitHub Repo : `https://github.com/NandoDP/questions-assemblee`

---

## ❓ Troubleshooting

### Problème : Superset ne démarre pas

**Solution** :
1. Vérifier les logs : erreur de connexion DB ?
2. Vérifier `DATABASE_URL` : doit commencer par `postgresql://`
3. Vérifier que `db-init.sql` a été exécuté

### Problème : Dashboard vide dans Flask

**Solution** :
1. Vérifier `SUPERSET_URL` dans les env vars
2. Vérifier `DASHBOARD_ID` correspond au dashboard créé
3. Tester l'URL Superset directement

### Problème : ETL GitHub Actions échoue

**Solution** :
1. Vérifier `DATABASE_URL` dans les secrets GitHub
2. Vérifier `API_TOKEN` est valide
3. Consulter les logs de l'action

### Problème : Accès refusé aux données dans Superset

**Solution** :
Configurer les permissions du rôle Public :
1. Settings → List Roles → Public
2. Ajouter permissions : `can_read`, `can_explore`
3. Supprimer permissions : `can_write`, `can_sql_json`

---

## 🚀 Prochaines Étapes

1. ✅ Personnaliser les dashboards Superset
2. ✅ Ajouter des alertes (webhook Discord/Slack)
3. ✅ Optimiser les requêtes SQL (vues matérialisées)
4. ✅ Ajouter authentification SSO (Google/GitHub)
5. ✅ Mettre en place CI/CD pour tests automatiques

---

## 📚 Ressources

- [Documentation Render](https://render.com/docs)
- [Documentation Superset](https://superset.apache.org/docs/intro)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [PostgreSQL on Render](https://render.com/docs/databases)

---

**Besoin d'aide ?** Ouvrir une issue sur GitHub ! 🙌
