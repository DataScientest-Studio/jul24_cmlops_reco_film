#!/bin/bash

# Exécute le premier script
python3 build_features.py

# Vérifie si le premier script a réussi
if [ $? -eq 0 ]; then
    # Exécute le deuxième script
    python3 data_to_db.py
else
    echo "Erreur lors de l'exécution de build_features.py"
    exit 1
fi