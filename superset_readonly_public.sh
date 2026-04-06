#!/bin/bash
# Script minimal pour un Superset public LECTURE SEULE (aucune exploration, aucun export)
# Ne pas arrêter en cas d'erreur (certaines commandes peuvent échouer normalement)
set +e

echo "🔒 Configuration Superset : accès strictement lecture seule pour Public..."

# 1. Créer le rôle Public s'il n'existe pas (db upgrade et init déjà faits avant)
superset fab create-role --role Public 2>/dev/null || echo "✓ Rôle Public existe déjà"

# 2. Ajouter uniquement les permissions de lecture minimale
READONLY_PERMS=(
    "can_read on Dashboard"
    "can_list on Dashboard"
    "can_get_embedded on Dashboard"
    "can_read on Chart"
    "can_list on Chart"
    "can_read on Dataset"
    "can_read on Database"
    "menu_access on Dashboards"
)
for perm in "${READONLY_PERMS[@]}"; do
    superset fab add-permission-role --role Public --permission "$perm" 2>/dev/null || true
done

echo "✅ Rôle Public = lecture seule. Aucun export, aucune exploration possible."
