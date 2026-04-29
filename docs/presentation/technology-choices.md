# Choix Technologiques et Alternatives

## Objectif

Cette note sert à expliquer pourquoi chaque technologie a été retenue pour construire une couche d'analyse au-dessus de `vie-publique.sn`, sans dépendre de son implémentation interne.

## 1. Python pour l'ETL et le NLP

Choix retenu: Python.

Pourquoi:
- même langage pour extraction web, traitement de données, validation, machine learning et chargement base.
- très bon écosystème pour les cas d'usage texte en français.
- vitesse de prototypage élevée.

Alternatives connues:
- Node.js: très bon pour l'I/O, moins naturel pour le NLP avancé.
- Java: robuste, mais trop lourd pour un produit analytique léger.
- outils ETL no-code: rapides au départ, moins flexibles sur une logique métier spécifique.

Décision pour `vie-publique.sn`:
- la source demande une logique d'extraction et de transformation spécifique, donc un langage généraliste orienté data était plus pertinent.

## 2. asyncio plutôt qu'un pipeline synchrone

Choix retenu: asyncio.

Pourquoi:
- la contrainte majeure est la latence réseau.
- permet d'accélérer la collecte sans déployer une architecture distribuée.

Alternatives connues:
- requests synchrone: plus simple, mais moins efficace si le volume monte.
- Spark: trop complexe pour ce volume.
- Airflow: excellent pour l'orchestration, mais pas nécessaire à cette échelle.

Décision pour `vie-publique.sn`:
- il fallait un pipeline rapide, simple et peu coûteux à exécuter quotidiennement.

## 3. PostgreSQL pour la couche analytique

Choix retenu: PostgreSQL.

Pourquoi:
- structure relationnelle adaptée aux questions, députés, ministères et zones géographiques.
- très bonne compatibilité BI avec Superset.
- vues SQL simples pour préparer les indicateurs.

Alternatives connues:
- MongoDB: souple, mais moins naturel pour les jointures analytiques.
- MySQL: possible, mais PostgreSQL est souvent plus confortable pour l'analytique.
- simple stockage fichiers: trop limité pour une plateforme consultable.

Décision pour `vie-publique.sn`:
- l'objectif était de produire des croisements analytiques fiables, pas seulement de conserver les données brutes.

## 4. CamemBERT pour la classification thématique

Choix retenu: CamemBERT.

Pourquoi:
- modèle francophone bien adapté au vocabulaire institutionnel.
- meilleure compréhension sémantique que les approches par mots-clés.
- réutilisable sur des textes parlementaires proches.

Alternatives connues:
- TF-IDF + Logistic Regression: plus léger, mais moins précis sémantiquement.
- mBERT: plus généraliste, moins ciblé sur le français.
- LLM via API: plus coûteux et moins stable pour une classification reproductible.

Décision pour `vie-publique.sn`:
- il fallait un modèle robuste sur des textes formels, avec une logique d'inférence batch maîtrisable.

## 5. Superset pour la BI

Choix retenu: Apache Superset.

Pourquoi:
- open source.
- connecté nativement à PostgreSQL.
- permet de produire vite des dashboards analytiques crédibles.
- supporte l'embed dans une interface dédiée.

Alternatives connues:
- Power BI: très connu, mais moins fluide pour un déploiement web public open source.
- Tableau: très puissant, mais plus coûteux.
- dashboard React sur mesure: plus flexible, mais beaucoup plus coûteux à développer.

Décision pour `vie-publique.sn`:
- la priorité était de délivrer rapidement de la valeur analytique sans recréer toute une couche BI.

## 6. Flask + React pour l'interface publique

Choix retenu: Flask pour l'API d'intégration, React pour l'interface publique.

Pourquoi:
- séparation claire entre analyse interne et consultation publique.
- backend léger pour gérer l'embed sécurisé Superset.
- frontend plus propre, plus mobile-friendly et mieux contrôlé qu'une exposition directe de Superset.

Alternatives connues:
- exposer Superset directement: plus rapide, moins propre en UX et en sécurité.
- Django: plus complet, mais inutilement lourd ici.
- site statique sans backend: insuffisant pour gérer les guest tokens et l'embed.

Décision pour `vie-publique.sn`:
- l'intégration devait être non intrusive, sécurisée et compatible avec une consultation publique simple.

## 7. Render pour l'hébergement

Choix retenu: Render.

Pourquoi:
- très simple pour héberger plusieurs services Docker.
- faible coût.
- suffisamment robuste pour une démonstration sérieuse.

Alternatives connues:
- AWS: plus riche, mais plus complexe à maintenir.
- Kubernetes: trop lourd pour ce périmètre.
- Heroku: proche, mais Render est bien adapté à cette architecture multi-services.

Décision pour `vie-publique.sn`:
- l'enjeu était d'avoir une plateforme en ligne rapidement, pas de construire une infrastructure complexe.

## 8. Intégration avec vie-publique.sn

Le point central est que l'intégration est externe et découplée.

Pourquoi c'est important:
- pas besoin de modifier la plateforme source.
- indépendance vis-à-vis de son implémentation technique.
- possibilité de faire évoluer la qualité analytique sans toucher au site d'origine.
- meilleure maîtrise des performances et de l'expérience publique.

Alternative la plus connue:
- intégration directe dans le CMS du site source.

Pourquoi ce n'était pas le bon choix ici:
- cela crée une dépendance forte au système existant.
- cela complique la maintenance.
- cela mélange publication éditoriale et analytique.

La logique retenue est donc:
- `vie-publique.sn` reste la source institutionnelle.
- ce projet agit comme une couche d'intelligence et de visualisation au-dessus de cette source.
