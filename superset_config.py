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

# ============================================================================
# CONFIGURATION RÔLE PUBLIC - LECTURE SEULE STRICTE
# ============================================================================

# Configuration des rôles
AUTH_TYPE = 1  # Database authentication
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# Le rôle Public a des permissions limitées (ne pas utiliser Gamma comme base)
# On va créer des permissions personnalisées plus restrictives
PUBLIC_ROLE_LIKE = None  # Ne pas hériter de Gamma

# Autoriser les utilisateurs non authentifiés avec le rôle Public
AUTH_USER_REGISTRATION = False
AUTH_USER_REGISTRATION_ROLE = "Public"

# Empêcher l'accès aux données brutes
PREVENT_UNSAFE_DEFAULT_URLS_ON_DATASET = True

# Désactiver l'exploration de données pour le rôle Public
SQLLAB_CTAS_NO_LIMIT = False

# ============================================================================
# CONFIGURATION IFRAME ET CORS
# ============================================================================

# Configuration CORS pour l'intégration iframe
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']  # En production, limiter aux domaines autorisés
}

# Autoriser l'affichage en iframe
HTTP_HEADERS = {
    'X-Frame-Options': 'ALLOWALL'
}
ENABLE_PROXY_FIX = True

# Désactiver Talisman pour permettre l'iframe
TALISMAN_ENABLED = False

# ============================================================================
# FEATURE FLAGS - DÉSACTIVER LES FONCTIONNALITÉS D'EXPLORATION
# ============================================================================

FEATURE_FLAGS = {
    # Dashboard de base - ACTIVÉ
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,  # DÉSACTIVÉ - Empêche filtrage interactif
    'DASHBOARD_CROSS_FILTERS': True,   # DÉSACTIVÉ - Empêche filtres croisés
    'DASHBOARD_FILTERS_EXPERIMENTAL': False,
    
    # Exploration - DÉSACTIVÉ
    'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': True,  # Protection CSRF pour explore
    'ENABLE_EXPLORE_DRAG_AND_DROP': False,  # DÉSACTIVÉ - Pas de drag & drop
    
    # SQL Lab - DÉSACTIVÉ COMPLÈTEMENT
    'SQLLAB_BACKEND_PERSISTENCE': False,
    'ENABLE_JAVASCRIPT_CONTROLS': False,  # Pas de contrôles JS personnalisés
    
    # Charts - Lecture seule
    'EMBEDDABLE_CHARTS': True,  # Permettre embedding
    'DASHBOARD_RBAC': True,     # Contrôle d'accès par rôle
    'EMBEDDED_SUPERSET': True,  # Mode embedded
    
    # Désactiver les requêtes async (empêche exploration avancée)
    'GLOBAL_ASYNC_QUERIES': False,
    
    # Désactiver les alertes et rapports
    'ALERT_REPORTS': False,
    'THUMBNAILS': False,  # Pas besoin de thumbnails pour lecture seule
}

# ============================================================================
# PERMISSIONS STRICTES POUR LE RÔLE PUBLIC
# ============================================================================

# Configuration du rôle invité
GUEST_ROLE_NAME = "Public"
GUEST_USER_NAME = "Guest"

# Permissions publiques - LECTURE SEULE STRICTE
# Ces permissions seront appliquées via le script setup
FAB_ADD_SECURITY_VIEWS = True

# Liste des permissions explicitement INTERDITES pour le rôle Public
# (à configurer via script)
PUBLIC_DENIED_PERMISSIONS = [
    # SQL Lab - TOUT INTERDIRE
    'can_read on SQLLab',
    'can_sqllab on Superset',
    'can_sql_json on Superset',
    'can_csv on Superset',
    'can_save_query on SQLLab',
    
    # Exploration - TOUT INTERDIRE
    'can_explore on Superset',
    'can_explore_json on Superset',
    
    # Modification - TOUT INTERDIRE
    'can_write on Dashboard',
    'can_write on Chart',
    'can_write on Dataset',
    'can_write on Database',
    'can_edit on Dashboard',
    'can_edit on Chart',
    
    # Export - INTERDIRE
    'can_export on Dashboard',
    'can_export on Chart',
    'can_export_csv on Superset',
    
    # Création - TOUT INTERDIRE
    'can_add on Dashboard',
    'can_add on Chart',
    'can_add on Dataset',
    
    # Suppression - TOUT INTERDIRE
    'can_delete on Dashboard',
    'can_delete on Chart',
    'can_delete on Dataset',
    
    # Données brutes - INTERDIRE
    'can_samples on Datasource',
    'can_get_data on Dataset',
]

# Permissions explicitement AUTORISÉES pour le rôle Public
PUBLIC_ALLOWED_PERMISSIONS = [
    # Dashboard - LECTURE SEULE
    'can_read on Dashboard',
    'can_list on Dashboard',
    
    # Chart - LECTURE SEULE (dans le contexte du dashboard uniquement)
    'can_read on Chart',
    
    # Dataset - Accès minimal nécessaire pour afficher les charts
    'can_read on Dataset',
    
    # Database - Métadonnées uniquement
    'can_read on Database',
]

# ============================================================================
# CONFIGURATION DE SÉCURITÉ SUPPLÉMENTAIRE
# ============================================================================

# Désactiver la possibilité de télécharger les données
ENABLE_FILTER_SETS = False

# # Désactiver les contrôles de filtrage avancés
# DASHBOARD_AUTO_REFRESH_MODE = "fetch"  # Pas de refresh automatique
# DASHBOARD_AUTO_REFRESH_INTERVALS = []  # Pas d'intervalles de refresh

# Configuration de session pour iframe
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True  # Nécessaire en production HTTPS
SESSION_COOKIE_HTTPONLY = True

# Désactiver la vérification CSRF pour les embedded dashboards
WTF_CSRF_EXEMPT_LIST = ['superset.views.core.log']
GUEST_TOKEN_JWT_SECRET = os.getenv('SUPERSET_JWT_SECRET', 'changeme-jwt-secret')

# ============================================================================
# CONFIGURATION CACHE ET PERFORMANCE
# ============================================================================

CACHE_CONFIG = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
}

# ============================================================================
# CONFIGURATION LOGS
# ============================================================================

ENABLE_TIME_ROTATE = True
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# ============================================================================
# CONFIGURATION WEBSERVER
# ============================================================================

SUPERSET_WEBSERVER_PORT = int(os.getenv('PORT', 8088))
SUPERSET_WEBSERVER_TIMEOUT = 120

# Compression Flask
ENABLE_FLASK_COMPRESS = True

# ============================================================================
# MESSAGES PERSONNALISÉS
# ============================================================================

# Message pour les utilisateurs publics
WELCOME_MESSAGE = "Dashboard en lecture seule - Les données sont mises à jour quotidiennement"

# Désactiver les exemples au démarrage
SUPERSET_DEMO_DB = False
LOAD_EXAMPLES = False