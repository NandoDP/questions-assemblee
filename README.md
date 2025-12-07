# 📊 Questions Parlementaires - Analyse & Dashboard

[![ETL Pipeline](https://github.com/NandoDP/questions-assemblee/actions/workflows/cron_etl.yml/badge.svg)](https://github.com/NandoDP/questions-assemblee/actions/workflows/cron_etl.yml)
[![CI](https://github.com/NandoDP/questions-assemblee/actions/workflows/ci.yml/badge.svg)](https://github.com/NandoDP/questions-assemblee/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Système automatisé d'analyse et de visualisation des questions parlementaires françaises avec classification ML et dashboard BI interactif.

⚠️ **Note importante** : Le modèle CamemBERT (422 MB) n'est pas inclus dans ce dépôt. Voir [models/camembert_model/README.md](models/camembert_model/README.md) pour les instructions de téléchargement.

---

## 🎯 Objectif

Ce projet collecte, analyse et visualise automatiquement les questions parlementaires de l'Assemblée Nationale Sénégalaise (XIVe législature). Il utilise un modèle de Machine Learning (CamemBERT) pour classifier les questions par thématique et génère des insights via un dashboard Apache Superset.

**Cas d'usage** :
- 📈 Suivi de l'activité parlementaire en temps réel
- 🔍 Analyse des sujets prioritaires par ministère
- 📊 Visualisation des délais de réponse gouvernementaux
- 🗺️ Cartographie des questions par région/département
- 🤖 Classification automatique des thématiques (ML)

---

## 🏗️ Architecture

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
│   - questions         │      │  - Dashboard BI          │
│   - deputes          │      │  - Charts & Metrics       │
│   - ministeres       │      └──────────┬───────────────┘
└───────────────────────┘                 │ iframe embed
                                          ↓
                               ┌──────────────────────────┐
                               │  Flask App (Web Service) │
                               │  - Dashboard Public      │
                               │  - Lecture seule         │
                               └──────────────────────────┘
```

### **Composants**

| Composant | Technologie | Hébergement | Rôle |
|-----------|-------------|-------------|------|
| **ETL Pipeline** | Python + asyncio | GitHub Actions | Extraction, transformation, classification ML |
| **Base de données** | PostgreSQL 15 | Render (Free) | Stockage des données structurées |
| **Dashboard BI** | Apache Superset | Render (Docker) | Création et visualisation des métriques |
| **Interface publique** | Flask | Render (Docker) | Dashboard public en lecture seule |
| **Classification ML** | CamemBERT (BERT FR) | Local / HuggingFace | Classification thématique des questions |

---

## 📈 Résultats

**Données collectées** :
- ✅ 250+ questions parlementaires analysées
- ✅ 165 députés suivis
- ✅ 26 ministères couverts
- ✅ Classification en 12+ thématiques principales

**Métriques clés** :
- 📊 Nombre de députés actifs : 33
- 📈 Taux de réponse : < 2%
- 🏆 Top 3 thématiques : Santé, Éducation, Culture
- 🗺️ Couverture géographique : 13/14 régions

---

## 🚀 Déploiement

### **🌐 Dashboard Public**

👉 **[Voir le dashboard en ligne](https://questions-assemblee-dashboard.onrender.com)**

Le dashboard est accessible publiquement en **lecture seule**. Aucun téléchargement de données brutes n'est possible pour les visiteurs.

### **⚡ Démarrage Rapide (Local)**

```bash
# Cloner le repo
git clone https://github.com/NandoDP/questions-assemblee.git
cd questions-assemblee

# Démarrer avec Docker Compose
docker-compose up -d

# Accéder aux services
open http://localhost:5000  # Dashboard public
open http://localhost:8088  # Superset admin (admin/admin123)
```

## 🛠️ Stack Technique

### **Backend & ETL**
- **Python 3.10** - Langage principal
- **asyncio / aiohttp** - Requêtes asynchrones API
- **asyncpg** - PostgreSQL async driver
- **Pydantic** - Validation des données
- **SQLAlchemy** - ORM

### **Machine Learning**
- **CamemBERT** (camembert-base) - Modèle BERT français
- **Transformers (HuggingFace)** - Framework ML
- **SpaCy** - NLP (entités nommées, lemmatisation)
- **Torch** - Deep Learning

### **Visualisation**
- **Apache Superset** - Dashboard BI
- **Flask** - Interface web publique
- **PostgreSQL 15** - Base de données

### **DevOps & CI/CD**
- **Docker** - Conteneurisation
- **GitHub Actions** - ETL automatisé (cron)
- **Render** - Hébergement cloud
- **Git LFS / HuggingFace Hub** - Gestion modèles ML

---

## 📊 Visualisations

### **Exemples de dashboards disponibles** :

La plateforme de visualisation offre plusieurs types de graphiques et tableaux de bord pour exploiter les données collectées :

#### **Métriques de performance parlementaire**

* **Indicateurs KPI** : Affichage des métriques clés (nombre total de questions, taux de réponse global, nombre de députés actifs) sous forme de cartes numériques pour un suivi rapide des performances.  
* **Évolution temporelle** : Graphiques en barres et courbes montrant l'évolution mensuelle du nombre de questions et de réponses, permettant d'identifier les périodes de forte activité parlementaire.

#### **Analyses thématiques**

* **Répartition par secteur** : Graphiques en secteurs (camembert) illustrant la distribution des questions par domaine (santé, éducation, économie, etc.), révélant les préoccupations prioritaires des députés.  
* **Nuage de mots-clés** : Visualisation des termes les plus fréquents dans les questions, facilitant l'identification des sujets récurrents et des tendances émergentes.

#### **Suivi de l'activité des députés**

* **Classement des plus actifs** : Tableaux de bord avec ranking des députés par nombre de questions posées et taux de réponse, permettant d'évaluer l'engagement parlementaire.  
* **Analyse par groupe parlementaire** : Graphiques comparatifs de l'activité par parti politique ou coalition.

#### **Dimension géographique**

* **Cartographie interactive** : Cartes choroplèthes du Sénégal montrant la répartition géographique des questions par région ou département, identifiant les zones les plus représentées dans les débats parlementaires.  
* **Heatmaps régionales** : Visualisation de l'intensité des préoccupations par zone géographique.

<!-- 1. **📊 Questions par Ministère** (Bar Chart)
   - Top 10 ministères par volume de questions
   - Évolution temporelle par ministère

2. **⏱️ Délais de Réponse** (KPI Cards + Line Chart)
   - Délai moyen de réponse
   - Évolution mensuelle
   - Comparaison entre ministères

3. **🗺️ Carte Géographique** (Map)
   - Questions par département
   - Heat map des zones actives

4. **🏷️ Thématiques Principales** (Pie Chart + Word Cloud)
   - Classification automatique par ML
   - Mots-clés fréquents

5. **👥 Top Députés** (Table + Bar Chart)
   - Députés les plus actifs
   - Taux de réponse par député

6. **📈 Timeline Interactive** (Timeline)
   - Évolution quotidienne/mensuelle
   - Filtres par parti, région, thématique -->

---

## 🔧 Fonctionnalités

### **✅ Déjà Implémenté**

- [x] Extraction automatique via API 👉 **[Vie Publique](https://www.vie-publique.sn/assemblee-nationale/questions)**
- [x] Pipeline ETL asynchrone optimisé
- [x] Classification ML avec CamemBERT fine-tuné
- [x] Extraction des entités nommées (ministères, lieux, dates)
- [-] Analyse de sentiment et score d'urgence
- [x] Base de données PostgreSQL avec vues optimisées
- [x] Dashboard Superset avec charts interactifs
- [x] Interface publique Flask (lecture seule)
- [x] ETL automatisé via GitHub Actions (cron quotidien)
- [x] Docker Compose pour dev local
- [x] Déploiement Render (Infrastructure as Code)

### **🚧 Roadmap**

- [ ] Alertes temps réel (webhook Discord/Slack)
- [ ] API REST publique pour accès aux données
- [ ] Analyse de séries temporelles (prédictions)
- [ ] Intégration d'autres sources (Sénat, débats)
- [ ] Authentification SSO (Google/GitHub)
- [ ] Tests unitaires et d'intégration (pytest)
- [ ] Monitoring avec Sentry
- [ ] Cache Redis pour Superset

---

## 📁 Structure du Projet

```
question-assemblee/
├── .github/workflows/        # GitHub Actions (CI/CD)
│   ├── cron_etl.yml         # ETL automatisé quotidien
│   ├── ci.yml               # Tests automatiques
│   └── build_and_push.yml   # Build images Docker
├── src/                     # Code source
│   ├── extractors/          # Extraction API
│   ├── transformers/        # Transformation & ML
│   ├── loaders/             # Chargement DB
│   ├── models/              # Modèles Pydantic
│   └── utils/               # Utilitaires
├── models/                  # Modèles ML
│   └── camembert_model/     # CamemBERT fine-tuné
├── Dockerfile.etl           # Image Docker ETL
├── Dockerfile.superset      # Image Docker Superset
├── Dockerfile.flask         # Image Docker Flask
├── docker-compose.yml       # Orchestration locale
├── render.yaml              # Déploiement Render
├── db-init.sql              # Schéma PostgreSQL
├── requirements.txt         # Dépendances Python
└── README.md                # Ce fichier
```

<!-- ---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amélioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité X'`)
4. Push la branche (`git push origin feature/amélioration`)
5. Ouvrir une Pull Request

---

## 📝 License

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails. -->

---

## 👤 Auteur

**Nando DP**
- GitHub : [@NandoDP](https://github.com/NandoDP)
- Portfolio : [À venir]

---

## 🙏 Remerciements

- **[Vie Publique](https://www.vie-publique.sn)** - Plateforme citoyenne du sénégal
<!-- 
---

## 📚 Documentation Complémentaire

- [QUICKSTART.md](QUICKSTART.md) - Démarrage rapide en local
- [DEPLOY.md](DEPLOY.md) - Guide de déploiement complet
- [MODEL_MANAGEMENT.md](MODEL_MANAGEMENT.md) - Gestion du modèle ML
- [models/camembert_model/README.md](models/camembert_model/README.md) - Téléchargement du modèle -->

---

**⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile !**
