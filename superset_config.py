# import os
# # from celery import Celery


# SUPERSET_JWT_SECRET = "hsdu&72hds88HH73jsKSkdhs&88sjsdh3PLUSLONGUEencore2024"

# # Configuration de la base de données
# # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://superset:superset@postgres:5432/superset')

# # Configuration Redis
# REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# # Configuration Celery
# class CeleryConfig:
#     CELERY_IMPORTS = ('superset.sql_lab', 'superset.tasks')
#     CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
#     BROKER_URL = REDIS_URL
#     CELERY_RESULT_BACKEND = REDIS_URL

# CELERY_CONFIG = CeleryConfig

# # Configuration de sécurité
# SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'your-secret-key-here')
# WTF_CSRF_ENABLED = True
# WTF_CSRF_TIME_LIMIT = None

# # Configuration des utilisateurs
# AUTH_TYPE = 1  # Database authentication
# AUTH_ROLE_ADMIN = 'Admin'
# AUTH_ROLE_PUBLIC = 'Public'

# # Configuration des permissions
# SUPERSET_WEBSERVER_DOMAINS = None
# ENABLE_PROXY_FIX = True

# # Configuration des uploads
# UPLOAD_FOLDER = '/app/superset_home/uploads'
# IMG_UPLOAD_FOLDER = '/app/superset_home/uploads'
# IMG_UPLOAD_URL = '/uploads/'

# # Configuration des features
# FEATURE_FLAGS = {
#     'ENABLE_TEMPLATE_PROCESSING': True,
#     'DASHBOARD_NATIVE_FILTERS': True,
#     'DASHBOARD_CROSS_FILTERS': True,
#     'DASHBOARD_FILTERS_EXPERIMENTAL': True,
#     'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': False,
#     'ENABLE_EXPLORE_DRAG_AND_DROP': True,
#     'GLOBAL_ASYNC_QUERIES': True,
# }

# # Configuration des visualisations
# DEFAULT_FEATURE_FLAGS = {
#     'CLIENT_CACHE': False,
#     'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': False,
#     'PRESTO_EXPAND_DATA': False,
# }

# # Configuration CORS pour l'intégration iframe
# ENABLE_CORS = True
# CORS_OPTIONS = {
#     'supports_credentials': True,
#     'allow_headers': ['*'],
#     'resources': ['*'],
#     'origins': ['*']
# }

# # Configuration des graphiques
# SUPERSET_CHART_PERMISSIONS = {
#     'can_read': ['Admin', 'Alpha', 'Gamma'],
#     'can_write': ['Admin', 'Alpha'],
# }

# Donner le rôle Gamma au rôle Public (lecture seule)
PUBLIC_ROLE_LIKE = "Gamma"

# Spécifie que les utilisateurs non connectés sont associés au rôle Public
AUTH_ROLE_PUBLIC = "Public"

SUPERSET_DATABASE_URI = "postgresql+psycopg2://airflow:airflow@postgres:5432/$questions"

# Autoriser l'affichage en iframe
ENABLE_X_FRAME_OPTIONS = False

# Pour les versions récentes de Superset, il faut aussi ajuster la CSP :
TALISMAN_ENABLED = False  # Désactive Flask-Talisman qui force la sécurité stricte

SUPERSET_JWT_SECRET = "hsdu&72hds88HH73jsKSkdhs&88sjsdh3PLUSLONGUEencore2024"

FEATURE_FLAGS = {
    "ALLOW_UPLOAD_CSV": True,
    # ... autres flags éventuels ...
}