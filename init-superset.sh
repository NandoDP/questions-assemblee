#!/bin/bash
set -e

echo "=== Initialisation de Superset sur Render ==="

# Vérifier que DATABASE_URL est défini
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Erreur: DATABASE_URL non défini"
    exit 1
fi

echo "✅ DATABASE_URL configuré"

# Initialiser la base de données Superset
echo "📦 Initialisation de la base de données Superset..."
superset db upgrade

# Créer un utilisateur admin (seulement si pas déjà créé)
echo "👤 Création de l'utilisateur admin..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@superset.com \
    --password ${SUPERSET_ADMIN_PASSWORD:-admin123} || echo "⚠️ Admin existe déjà"

# Créer un utilisateur public en lecture seule
echo "👥 Configuration des rôles..."
superset init

# Importer les rôles personnalisés (optionnel)
# superset import_roles -p /app/roles.json

echo "✅ Initialisation terminée"

# Démarrer Superset
echo "🚀 Démarrage de Superset..."
gunicorn \
    --bind 0.0.0.0:${PORT:-8088} \
    --workers ${SUPERSET_WORKERS:-4} \
    --timeout 120 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "superset.app:create_app()"
