import os

# Configuration de la base de données
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/superset')

# Si Render utilise postgres://, le convertir en postgresql://
if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

# Configuration de sécurité
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'changeme-secret-key-production')
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Configuration JWT pour dashboard public
SUPERSET_JWT_SECRET = os.getenv('SUPERSET_JWT_SECRET', 'changeme-jwt-secret')

# Configuration des rôles
AUTH_TYPE = 1  # Database authentication
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# Donner le rôle Gamma au rôle Public (lecture seule)
PUBLIC_ROLE_LIKE = "Gamma"

# Autoriser les utilisateurs non authentifiés avec le rôle Public
AUTH_USER_REGISTRATION = False
AUTH_USER_REGISTRATION_ROLE = "Public"

# Configuration CORS pour l'intégration iframe
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']
}

# Autoriser l'affichage en iframe
HTTP_HEADERS = {
    'X-Frame-Options': 'ALLOWALL'
}
ENABLE_PROXY_FIX = True

# Désactiver Talisman pour permettre l'iframe
TALISMAN_ENABLED = False

# Configuration des features
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_FILTERS_EXPERIMENTAL': False,
    'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': False,
    'ENABLE_EXPLORE_DRAG_AND_DROP': True,
    'GLOBAL_ASYNC_QUERIES': False,  # Redis requis si True
    'EMBEDDABLE_CHARTS': True,
    'DASHBOARD_RBAC': True,
}

# Configuration des permissions pour le rôle Public
# Désactiver l'accès aux données brutes pour les utilisateurs publics
PREVENT_UNSAFE_DEFAULT_URLS_ON_DATASET = True

# Configuration de cache (optionnel, nécessite Redis)
CACHE_CONFIG = {
    'CACHE_TYPE': 'simple',  # Utiliser 'redis' si vous ajoutez Redis
}

# Configuration des logs
ENABLE_TIME_ROTATE = True
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configuration du webserver
SUPERSET_WEBSERVER_PORT = int(os.getenv('PORT', 8088))
SUPERSET_WEBSERVER_TIMEOUT = 120

# Désactiver les exemples au démarrage
ENABLE_FLASK_COMPRESS = True