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

# Configurer le rôle Public en lecture seule (script Python rapide ~5s)
echo "🔒 Configuration du rôle Public en lecture seule..."
python /app/docker/configure_public_role.py || echo "⚠️ Échec config Public (non bloquant)"

# Assigner le rôle Public à tous les datasets
echo "📊 Attribution du rôle Public aux datasets..."
python /app/docker/assign_public_to_datasets.py || echo "⚠️ Échec attribution datasets (non bloquant)"

# Créer l'utilisateur guest pour accès public
echo "👤 Création de l'utilisateur guest..."
python /app/docker/create_guest_user.py || echo "⚠️ Échec création guest (non bloquant)"

echo "✅ Initialisation terminée"

# Démarrer Superset
echo "🚀 Démarrage de Superset sur le port ${PORT:-8088}..."
echo "📡 Bind address: 0.0.0.0:${PORT:-8088}"

# Démarrer Gunicorn avec configuration optimisée pour Render Free tier
# - 1 worker (plus rapide à démarrer, suffisant pour Free tier)
# - preload pour charger l'app avant fork
# - timeout augmenté pour le premier démarrage
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8088} \
    --workers 1 \
    --worker-class gthread \
    --threads 4 \
    --timeout 300 \
    --graceful-timeout 120 \
    --keep-alive 5 \
    --preload \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "superset.app:create_app()"