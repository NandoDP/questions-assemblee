# 🚀 Démarrage Rapide

Guide pour tester le projet en local avant déploiement sur Render.

## 📋 Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installé et démarré
- [Git](https://git-scm.com/) installé
- [Python 3.10+](https://www.python.org/downloads/) (optionnel, pour ETL local)

---

## ⚡ Démarrage Local (Docker Compose)

### 1. Cloner le repo

```bash
git clone https://github.com/NandoDP/questions-assemblee.git
cd questions-assemblee
```

### 2. Créer le fichier .env

```bash
cp .env.example .env
```

Éditer `.env` et ajouter votre token API :
```env
API_TOKEN=votre_token_api_ici
```

### 3. Télécharger le modèle ML (si disponible)

```bash
# Option A : Depuis HuggingFace
python download_model.py

# Option B : Téléchargement manuel
# Placer model.safetensors dans models/camembert_model/
```

### 4. Démarrer les services

```bash
docker-compose up -d
```

Cela va démarrer :
- ✅ PostgreSQL sur port 5432
- ✅ Superset sur port 8088
- ✅ Flask App sur port 5000

### 5. Suivre les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f superset
```

### 6. Attendre l'initialisation

⏳ **Superset prend 2-3 minutes pour démarrer**

Vérifier que les services sont prêts :
```bash
# PostgreSQL
docker-compose exec postgres pg_isready

# Superset
curl http://localhost:8088/health

# Flask
curl http://localhost:5000/health
```

### 7. Accéder aux services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard Public** | http://localhost:5000 | Aucun (public) |
| **Superset Admin** | http://localhost:8088 | admin / admin123 |
| **PostgreSQL** | localhost:5432 | postgres / postgres |

---

## 🗄️ Vérifier la Base de Données

### Via psql

```bash
# Se connecter
docker-compose exec postgres psql -U postgres -d questions_assemblee

# Lister les tables
\dt

# Vérifier les données
SELECT COUNT(*) FROM questions;
SELECT COUNT(*) FROM deputes;

# Quitter
\q
```

### Via DBeaver / pgAdmin

- **Host** : localhost
- **Port** : 5432
- **Database** : questions_assemblee
- **User** : postgres
- **Password** : postgres

---

## 🔄 Exécuter l'ETL Localement

### Option A : Avec Docker

```bash
# Décommenter le service etl dans docker-compose.yml
docker-compose up etl
```

### Option B : Sans Docker

```bash
# Installer les dépendances
pip install -r requirements.txt
python -m spacy download fr_core_news_sm

# Configurer les variables d'environnement
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/questions_assemblee
export API_TOKEN=votre_token

# Exécuter l'ETL
python -m src.pipeline.etl_pipeline
```

---

## 📊 Configurer Superset

### 1. Se connecter à Superset

URL : http://localhost:8088
- Username : `admin`
- Password : `admin123`

### 2. Ajouter la source de données

1. **Settings** → **Database Connections** → **+ Database**
2. Sélectionner **PostgreSQL**
3. Remplir :
   ```
   Display Name: Questions Assemblée
   SQLAlchemy URI: postgresql://postgres:postgres@postgres:5432/questions_assemblee
   ```
4. **Test Connection** → **Connect**

### 3. Créer un Dataset

1. **Data** → **Datasets** → **+ Dataset**
2. **Database** : Questions Assemblée
3. **Schema** : public
4. **Table** : `questions` ou `vue_questions_complete`
5. **Save**

### 4. Créer des Charts

Exemples de graphiques :

#### A. Questions par Ministère (Bar Chart)
- **Chart Type** : Bar Chart
- **X-Axis** : `ministere_attributaire`
- **Metric** : COUNT(*)
- **Sort** : Descending

#### B. Évolution Temporelle (Line Chart)
- **Chart Type** : Line Chart
- **X-Axis** : `date_publication` (Temporal, grain: Month)
- **Metric** : COUNT(*)

#### C. Répartition Thématique (Pie Chart)
- **Chart Type** : Pie Chart
- **Dimension** : `thematique_principale`
- **Metric** : COUNT(*)

#### D. Délai de Réponse Moyen (Big Number)
- **Chart Type** : Big Number
- **Metric** : AVG(`delai_reponse_jours`)

### 5. Créer un Dashboard

1. **Dashboards** → **+ Dashboard**
2. Nommer : `Questions Parlementaires`
3. Glisser-déposer les charts créés
4. **Save**
5. Noter le **Dashboard ID** dans l'URL (ex: `/dashboard/1/`)

### 6. Mettre à jour Flask

Éditer `.env` ou `docker-compose.yml` :
```env
DASHBOARD_ID=1
```

Redémarrer Flask :
```bash
docker-compose restart flask
```

---

## 🛑 Arrêter les Services

```bash
# Arrêter tous les services
docker-compose down

# Arrêter ET supprimer les volumes (données)
docker-compose down -v
```

---

## 🔧 Commandes Utiles

### Reconstruire les images

```bash
# Tous les services
docker-compose build

# Un service spécifique
docker-compose build superset
```

### Redémarrer un service

```bash
docker-compose restart superset
```

### Exécuter une commande dans un conteneur

```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres

# Superset
docker-compose exec superset superset --help

# Flask
docker-compose exec flask flask --help
```

### Nettoyer Docker

```bash
# Supprimer les conteneurs arrêtés
docker container prune

# Supprimer les images non utilisées
docker image prune

# Nettoyer tout
docker system prune -a --volumes
```

---

## 🐛 Troubleshooting

### Superset ne démarre pas

```bash
# Voir les logs
docker-compose logs superset

# Vérifier que PostgreSQL est prêt
docker-compose exec postgres pg_isready

# Redémarrer Superset
docker-compose restart superset
```

### Port déjà utilisé

Si le port 5432, 8088 ou 5000 est déjà utilisé :

```bash
# Vérifier les ports utilisés
netstat -an | findstr "5432"  # Windows
lsof -i :5432                  # Mac/Linux

# Modifier les ports dans docker-compose.yml
ports:
  - "15432:5432"  # PostgreSQL
  - "18088:8088"  # Superset
  - "15000:5000"  # Flask
```

### Modèle ML manquant

Si l'ETL échoue avec "model not found" :

```bash
# Télécharger le modèle
python download_model.py

# OU utiliser un volume Docker
docker-compose up etl -v ./models:/app/models
```

---

## ✅ Prêt pour le Déploiement

Une fois que tout fonctionne en local :

1. ✅ PostgreSQL fonctionne
2. ✅ Superset affiche les dashboards
3. ✅ Flask embed le dashboard correctement
4. ✅ ETL ajoute des données

👉 **Suivre le guide [DEPLOY.md](DEPLOY.md) pour déployer sur Render**

---

## 📚 Ressources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Superset Docs](https://superset.apache.org/docs/intro)
- [Flask Docs](https://flask.palletsprojects.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
