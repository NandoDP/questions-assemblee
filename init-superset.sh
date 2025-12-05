#!/bin/bash
set -e

echo "=== Initialisation de Superset ==="

# Attendre que PostgreSQL soit pr�t
# echo "Attente de PostgreSQL..."
# while ! nc -z postgres 5432; do
#   sleep 1
# done
# echo "PostgreSQL est pr�t!"

# Initialiser la base de donn�es Superset
echo "Initialisation de la base de donn�es Superset..."
superset db upgrade

# Cr�er un utilisateur admin
echo "Cr�ation de l'utilisateur admin..."
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password admin

# echo "Chargement des exemples..."
# superset load_examples

echo "Initialiser"
superset init

echo "=== Initialisation termin�e ==="
