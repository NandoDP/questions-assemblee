#!/bin/bash
# Script minimal pour un Superset public LECTURE SEULE (aucune exploration, aucun export)
set -e

echo "🔒 Configuration Superset : accès strictement lecture seule pour Public..."

# 1. Initialiser la base et le rôle Public
superset db upgrade
superset init
superset fab create-role --role Public 2>/dev/null || echo "Rôle Public existe déjà"

# 2. Supprimer toutes les permissions du rôle Public
ALL_PERMS=$(superset fab list-permissions | awk '{print $1" on "$3}' | grep -v '^$')
for perm in $ALL_PERMS; do
    superset fab delete-permission-role --role Public --permission "$perm" 2>/dev/null || true
done

# 3. Ajouter uniquement les permissions de lecture minimale
READONLY_PERMS=(
    "can_read on Dashboard"
    "can_list on Dashboard"
    "can_get_embedded on Dashboard"
    "can_read on Chart"
    "can_list on Chart"
    "can_read on Dataset"
    "can_read on Database"
    "can_read on SavedQuery"
    "can_userinfo on UserDBModelView"
    "menu_access on Dashboards"
)
for perm in "${READONLY_PERMS[@]}"; do
    superset fab add-permission-role --role Public --permission "$perm" 2>/dev/null || true
done

echo "✅ Rôle Public = lecture seule. Aucun export, aucune exploration possible."
