# Questions Parlementaires

Système d'analyse automatisée des questions parlementaires publiées sur [vie-publique.sn](https://www.vie-publique.sn/assemblee-nationale/questions), avec enrichissement NLP, stockage structuré et visualisation publique en lecture seule.

Le projet transforme une source web institutionnelle en un dispositif de suivi exploitable par un lecteur non technique: activité parlementaire, ministères les plus sollicités, thématiques dominantes, couverture territoriale et qualité de réponse gouvernementale.

## Vue d'Ensemble

- Source: questions publiées sur `vie-publique.sn`
- Pipeline: extraction, validation, enrichissement, chargement PostgreSQL
- Intelligence: classification thématique avec CamemBERT
- Restitution: dashboard public embarqué via Superset
- Déploiement: Render + GitHub Actions

## Objectif Produit

L'objectif n'est pas seulement de stocker des données, mais de produire un outil de lecture augmentée de l'activité parlementaire.

Le système permet de:
- suivre le volume et l'évolution des questions parlementaires,
- identifier les ministères et sujets les plus sollicités,
- visualiser les écarts de réponse,
- lire les dynamiques régionales,
- rendre les données compréhensibles à travers une interface publique simple.

## Architecture

```text
vie-publique.sn
    -> extracteurs Python async
    -> normalisation / validation
    -> enrichissement NLP / classification ML
    -> PostgreSQL
    -> Apache Superset
    -> Flask + React (embed public)
```

## Résultats Obtenus

- Plus de 250 questions parlementaires intégrées
- 165 députés suivis
- 26 ministères couverts
- 12+ thématiques principales classifiées
- Couverture géographique sur 13 régions sur 14

## Choix Technologiques et Alternatives

### Python pour l'ETL

Choix retenu: `Python`

Pourquoi:
- excellent écosystème pour scraping, data engineering et NLP dans un même langage,
- très bon compromis entre vitesse de développement et lisibilité,
- intégration directe avec `Transformers`, `spaCy`, `Pydantic` et PostgreSQL.

Alternatives courantes:
- `Node.js`: bon pour l'I/O, moins naturel ici pour la partie NLP/ML,
- `Java`: robuste mais surdimensionné pour un prototype analytique rapide,
- `Airbyte` ou `Talend`: adaptés aux connecteurs standard, moins souples pour une logique métier sur mesure.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- la source nécessite une extraction et une transformation métier spécifiques,
- il fallait unifier scraping, nettoyage textuel, classification et chargement DB dans une seule chaîne simple.

### asyncio plutôt qu'un ETL synchrone

Choix retenu: `asyncio` / requêtes asynchrones

Pourquoi:
- réduit le temps d'extraction sur une source web avec latence réseau,
- garde le pipeline léger sans nécessiter une infra lourde.

Alternatives courantes:
- script synchrone `requests`: plus simple mais moins performant si le volume augmente,
- `Spark`: trop lourd pour ce volume et ce contexte,
- `Airflow`: très bon orchestrateur, mais trop coûteux en complexité pour un cas d'usage encore compact.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- la contrainte principale est l'attente réseau, pas le calcul distribué.

### PostgreSQL plutôt que MongoDB ou fichiers plats

Choix retenu: `PostgreSQL`

Pourquoi:
- modèle relationnel adapté aux entités du domaine: questions, députés, ministères, régions,
- requêtes analytiques et vues SQL faciles à exposer à Superset,
- bon équilibre entre simplicité, robustesse et coût.

Alternatives courantes:
- `MongoDB`: flexible mais moins naturel pour les jointures analytiques et la BI,
- `MySQL`: viable, mais PostgreSQL offre en pratique un meilleur confort pour requêtes analytiques et extensions,
- fichiers CSV/Parquet seuls: utiles en stockage intermédiaire, insuffisants pour un service BI vivant.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- les données publiées doivent être restructurées et croisées pour produire des indicateurs fiables.

### CamemBERT plutôt que TF-IDF ou un modèle généraliste

Choix retenu: `CamemBERT`

Pourquoi:
- modèle francophone pertinent pour des textes parlementaires en français,
- meilleure compréhension sémantique qu'une approche purement lexicale,
- classification plus robuste sur des formulations administratives et politiques.

Alternatives courantes:
- `TF-IDF + Logistic Regression`: plus léger, mais moins précis sur la sémantique,
- `mBERT`: plus généraliste, moins spécialisé pour le français,
- `GPT API`: puissant mais plus coûteux, moins contrôlable, et moins adapté à une classification batch stable.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- les questions parlementaires utilisent un langage formel, souvent ambigu si l'on se limite aux mots-clés.

### Superset plutôt que Power BI, Tableau ou dashboards maison

Choix retenu: `Apache Superset`

Pourquoi:
- open source,
- connecté nativement à PostgreSQL,
- très rapide pour construire des dashboards analytiques sans recréer toute une couche de visualisation,
- facile à embarquer dans un site public.

Alternatives courantes:
- `Power BI`: très connu mais moins naturel pour une intégration web publique open source,
- `Tableau`: excellent, mais plus coûteux et moins aligné avec un déploiement léger indépendant,
- `React + Recharts/ECharts` uniquement: plus flexible visuellement, mais demande de reconstruire toute la couche BI.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- le besoin prioritaire était d'aller vite vers une restitution analytique crédible, pas de développer un front BI sur mesure dès le départ.

### Flask + React pour l'interface publique plutôt qu'un simple lien Superset

Choix retenu: `Flask` pour l'API d'intégration et `React` pour l'expérience publique

Pourquoi:
- contrôle fin de l'authentification embed Superset,
- possibilité d'exposer un site propre, en lecture seule, découplé de l'interface d'administration Superset,
- adaptation mobile et choix d'affichage selon le contexte.

Alternatives courantes:
- exposer Superset directement: plus rapide, mais moins maîtrisé côté UX, sécurité et branding,
- `Django`: bon framework complet, mais plus lourd qu'utile ici,
- front statique sans backend: insuffisant pour gérer les guest tokens et l'embed sécurisé.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- l'intégration visée devait rester non intrusive, publique, compatible mobile et séparée de l'interface d'analyse interne.

### Render plutôt qu'AWS ou Kubernetes

Choix retenu: `Render`

Pourquoi:
- déploiement simple pour plusieurs services Docker,
- coût réduit,
- adapté à une démonstration sérieuse sans surcharge DevOps.

Alternatives courantes:
- `AWS`: plus puissant, mais plus complexe à exploiter pour cette taille de projet,
- `Kubernetes`: pertinent à grande échelle, trop lourd ici,
- `Heroku`: comparable, mais Render donne une bonne simplicité sur ce montage multi-services.

Pourquoi c'était pertinent pour `vie-publique.sn`:
- l'enjeu était de livrer vite une plateforme consultable, pas d'optimiser une infra cloud avancée.

## Intégration à vie-publique.sn

L'intégration a été pensée comme une intégration externe, propre et peu invasive.

Le projet ne modifie pas `vie-publique.sn`. Il s'appuie sur ses publications comme source de données, les restructure dans une base dédiée, puis expose une lecture enrichie dans un dashboard autonome.

Ce choix présente trois avantages:
- pas de dépendance forte au système interne du site source,
- possibilité d'améliorer l'analyse sans toucher à la plateforme éditoriale,
- meilleure maîtrise de la qualité des données, de la fréquence de mise à jour et de l'expérience utilisateur.

## Structure du Dépôt

```text
question-assemblee/
├── dashboard-react/        application publique et backend d'embed
├── docs/                   documentation de présentation et d'exploitation
├── scripts/                scripts techniques regroupés par usage
├── models/                 modèle CamemBERT et artefacts associés
├── src/                    pipeline ETL et logique métier
├── db-init.sql             schéma PostgreSQL
├── docker-compose.yml      stack locale
├── Dockerfile.*            images de services
├── render.yaml             déploiement Render
└── superset_config.py      configuration Superset
```

## Documentation

- [Index documentation](docs/README.md)
- [Choix technologiques et alternatives](docs/presentation/technology-choices.md)
- [Guide de démarrage local](docs/operations/QUICKSTART.md)
- [Guide de déploiement](docs/operations/DEPLOY.md)

Les scripts techniques qui étaient auparavant visibles à la racine ont été regroupés dans `scripts/`:
- `scripts/superset/` pour le bootstrap et l'administration Superset,
- `scripts/ml/` pour la gestion du modèle,
- `scripts/legacy/` pour les prototypes archivés.

## Démonstration

- Dashboard public: [https://questions-assemblee-dashboard.onrender.com](https://questions-assemblee-dashboard.onrender.com)
- Source exploitée: [https://www.vie-publique.sn/assemblee-nationale/questions](https://www.vie-publique.sn/assemblee-nationale/questions)

## Auteur

- GitHub: [@NandoDP](https://github.com/NandoDP)
