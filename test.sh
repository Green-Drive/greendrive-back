#!/bin/bash

# Vérifier si l'API est en cours d'exécution
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "L'API n'est pas en cours d'exécution. Veuillez d'abord démarrer l'application avec ./start.sh"
    exit 1
fi

# Exécuter les tests
echo "Exécution des tests..."
python3 test_api.py 