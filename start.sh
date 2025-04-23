#!/bin/bash

# Démarrer les conteneurs Docker
echo "Démarrage des conteneurs Docker..."
docker-compose up -d

# Attendre que PostgreSQL soit prêt
echo "Attente que PostgreSQL soit prêt..."
sleep 5

# Initialiser la base de données
echo "Initialisation de la base de données..."
python init_db.py

# Démarrer l'application FastAPI
echo "Démarrage de l'application FastAPI..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 