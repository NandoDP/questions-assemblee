# ✅ Checklist Déploiement Render

Utilisez cette checklist pour suivre votre progression lors du déploiement.

---

## 📋 Pré-déploiement

### Vérifications locales

- [ ] Docker Desktop installé et démarré
- [ ] `docker-compose up -d` fonctionne sans erreur
- [ ] PostgreSQL accessible (localhost:5432)
- [ ] Superset démarre correctement (localhost:8088)
- [ ] Flask affiche le dashboard (localhost:5000)
- [ ] ETL s'exécute sans erreur (test manuel)
- [ ] Modèle CamemBERT téléchargé ou disponible sur HuggingFace

### Vérifications Git

- [ ] `.env` est dans `.gitignore` (ne PAS push les secrets)
- [ ] `model.safetensors` est dans `.gitignore`
- [ ] Tous les fichiers sont commit
- [ ] Push sur GitHub réussi
- [ ] GitHub Actions workflows visibles dans l'onglet Actions

---

## ☁️ Déploiement Render

### Étape 1 : PostgreSQL

- [ ] Compte Render créé
- [ ] PostgreSQL créé (Free tier)
- [ ] Nom : `questions-assemblee-db`
- [ ] Region : Frankfurt
- [ ] **Internal Database URL** copié
- [ ] **External Database URL** copié
- [ ] Connexion testée via psql ou DBeaver
- [ ] Script `db-init.sql` exécuté
- [ ] Tables créées (vérifier avec `\dt`)
- [ ] Départements insérés (45 rows)

**Commande de vérification** :
```sql
SELECT COUNT(*) FROM questions;
SELECT COUNT(*) FROM deputes;
SELECT COUNT(*) FROM ministeres;
SELECT COUNT(*) FROM departements;
```

---

### Étape 2 : Apache Superset

- [ ] Web Service créé
- [ ] Nom : `questions-assemblee-superset`
- [ ] Runtime : Docker
- [ ] Dockerfile : `Dockerfile.superset`
- [ ] Branch : `main`
- [ ] Region : Frankfurt
- [ ] **Variables d'environnement configurées** :
  - [ ] `DATABASE_URL` (Internal URL de PostgreSQL)
  - [ ] `SUPERSET_SECRET_KEY` (généré avec openssl)
  - [ ] `SUPERSET_JWT_SECRET` (généré avec openssl)
  - [ ] `SUPERSET_ADMIN_PASSWORD` (choisi)
  - [ ] `PORT` (8088 - auto)
- [ ] Health Check Path : `/health`
- [ ] Déploiement lancé
- [ ] Logs suivis (attendre 5-10 min)
- [ ] Service démarré sans erreur
- [ ] URL Superset accessible
- [ ] Login admin fonctionne

**URL** : `https://questions-assemblee-superset.onrender.com`

---

### Étape 3 : Configuration Superset

- [ ] Connexion à Superset (admin/password)
- [ ] Database Connection ajoutée :
  - [ ] Type : PostgreSQL
  - [ ] Display Name : `Questions Assemblée`
  - [ ] SQLAlchemy URI : Internal URL (remplacer `postgres://` par `postgresql://`)
  - [ ] Test Connection : ✅ Success
  - [ ] Save
- [ ] Dataset créé :
  - [ ] Table : `questions` ou `vue_questions_complete`
  - [ ] Save
- [ ] Charts créés :
  - [ ] Questions par Ministère (Bar Chart)
  - [ ] Évolution Temporelle (Line Chart)
  - [ ] Thématiques (Pie Chart)
  - [ ] Délai Moyen (Big Number)
  - [ ] (Optionnel) Carte géographique
- [ ] Dashboard créé :
  - [ ] Nom : `Questions Parlementaires`
  - [ ] Charts ajoutés au dashboard
  - [ ] Layout organisé
  - [ ] Save
- [ ] Dashboard rendu public :
  - [ ] `...` → Share → Public
  - [ ] URL copiée (format : `/superset/dashboard/1/?standalone=true`)
  - [ ] **Dashboard ID noté** : `____`

---

### Étape 4 : Flask App

- [ ] Web Service créé
- [ ] Nom : `questions-assemblee-dashboard`
- [ ] Runtime : Docker
- [ ] Dockerfile : `Dockerfile.flask`
- [ ] Branch : `main`
- [ ] Region : Frankfurt
- [ ] **Variables d'environnement configurées** :
  - [ ] `SUPERSET_URL` (URL Superset complet)
  - [ ] `DASHBOARD_ID` (ID du dashboard créé)
  - [ ] `FLASK_SECRET_KEY` (généré)
  - [ ] `PORT` (5000 - auto)
- [ ] Health Check Path : `/health`
- [ ] Déploiement lancé
- [ ] Service démarré sans erreur
- [ ] URL Flask accessible
- [ ] Dashboard embedded correctement

**URL** : `https://questions-assemblee-dashboard.onrender.com`

---

### Étape 5 : GitHub Actions (ETL)

- [ ] Aller sur GitHub → Settings → Secrets and variables → Actions
- [ ] **Secrets ajoutés** :
  - [ ] `DATABASE_URL` (Internal URL de Render PostgreSQL)
  - [ ] `API_TOKEN` (Token API Assemblée Nationale)
  - [ ] `GHCR_TOKEN` (Personal Access Token - si images Docker)
- [ ] Workflow `cron_etl.yml` visible dans Actions
- [ ] Test manuel du workflow :
  - [ ] Actions → Scheduled ETL Pipeline
  - [ ] Run workflow → Run workflow
  - [ ] Attendre la fin (5-10 min)
  - [ ] ✅ Success
  - [ ] Logs consultés (pas d'erreur)
- [ ] Vérifier les données dans PostgreSQL :
  ```sql
  SELECT COUNT(*) FROM questions WHERE date_creation > NOW() - INTERVAL '1 day';
  ```
- [ ] Vérifier que le cron est actif (schedule: `0 2 * * *`)

---

## 🎉 Tests de Validation

### Tests fonctionnels

- [ ] **PostgreSQL** :
  ```bash
  psql "postgresql://user:pass@host/db" -c "SELECT COUNT(*) FROM questions;"
  ```
  Résultat attendu : > 0

- [ ] **Superset** :
  ```bash
  curl https://questions-assemblee-superset.onrender.com/health
  ```
  Résultat attendu : `200 OK`

- [ ] **Flask** :
  ```bash
  curl https://questions-assemblee-dashboard.onrender.com/health
  ```
  Résultat attendu : `{"status": "healthy"}`

- [ ] **Dashboard Public** :
  - [ ] Ouvrir l'URL Flask dans un navigateur
  - [ ] Dashboard Superset chargé dans iframe
  - [ ] Graphiques interactifs fonctionnent
  - [ ] Pas d'accès au SQL Lab (lecture seule)

### Tests de sécurité

- [ ] Aucun téléchargement de données brutes possible
- [ ] SQL Lab inaccessible pour les visiteurs
- [ ] Dashboard accessible sans authentification
- [ ] Variables d'environnement sensibles NON exposées

---

## 📊 Monitoring

### Vérifications quotidiennes

- [ ] GitHub Actions ETL s'exécute chaque jour à 2h UTC
- [ ] Logs GitHub Actions : aucune erreur
- [ ] Données mises à jour dans PostgreSQL
- [ ] Dashboard Superset affiche les nouvelles données

### Limites Plan Free

- [ ] **PostgreSQL** : 256 MB (vérifier usage)
- [ ] **Web Services** : 750h/mois (services s'endorment après 15 min)
- [ ] **Build Minutes** : 500 min/mois

**Upgrade si nécessaire** : $7/mois par service

---

## 📝 Documentation

### Fichiers à mettre à jour

- [ ] README.md : URL du dashboard public
- [ ] DEPLOY.md : Screenshots des dashboards
- [ ] Badges GitHub Actions (vert si tout fonctionne)

### Portfolio

- [ ] Capturer screenshots des dashboards
- [ ] Documenter les métriques clés
- [ ] Ajouter lien vers repo GitHub dans CV/Portfolio
- [ ] (Optionnel) Article de blog sur Medium/Dev.to

---

## 🎓 Améliorations Futures

### Court terme (1-2 semaines)

- [ ] Ajouter plus de visualisations dans Superset
- [ ] Optimiser les requêtes SQL (index, vues matérialisées)
- [ ] Ajouter tests unitaires (pytest)
- [ ] Mettre en place monitoring (Sentry)

### Moyen terme (1-2 mois)

- [ ] API REST publique pour accès aux données
- [ ] Alertes Slack/Discord pour anomalies
- [ ] Cache Redis pour Superset
- [ ] Authentification SSO (Google/GitHub)

### Long terme (3+ mois)

- [ ] Analyse prédictive (ML pour prédire délais de réponse)
- [ ] Intégration d'autres sources (Sénat, débats)
- [ ] Visualisations avancées (D3.js, Plotly)
- [ ] Application mobile (React Native / Flutter)

---

## ✅ Validation Finale

**Avant de considérer le projet comme terminé** :

- [ ] Tous les services Render déployés et fonctionnels
- [ ] Dashboard public accessible et performant
- [ ] ETL automatisé s'exécute sans erreur
- [ ] Documentation complète (README, DEPLOY, QUICKSTART)
- [ ] Code poussé sur GitHub
- [ ] Screenshots ajoutés au README
- [ ] Projet ajouté au portfolio / CV

---

## 🚀 Liens Utiles

| Service | URL | Status |
|---------|-----|--------|
| Dashboard Public | https://questions-assemblee-dashboard.onrender.com | [ ] Live |
| Superset Admin | https://questions-assemblee-superset.onrender.com | [ ] Live |
| GitHub Repo | https://github.com/NandoDP/questions-assemblee | [ ] Public |
| GitHub Actions | https://github.com/NandoDP/questions-assemblee/actions | [ ] Green |

---

**🎉 Félicitations ! Votre projet est maintenant en production !**

Pour toute question, ouvrir une issue sur GitHub.
