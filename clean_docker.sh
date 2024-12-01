#!/bin/bash

# Script de nettoyage Docker

echo "=============================="
echo " Nettoyage de l'environnement Docker"
echo "=============================="

# Fonction pour afficher le menu
function display_menu() {
    echo "Choisissez une option :"
    echo "1) Supprimer les conteneurs arrêtés"
    echo "2) Supprimer les images non utilisées"
    echo "3) Supprimer les réseaux non utilisés"
    echo "4) Supprimer les volumes non utilisés"
    echo "5) Prune complet (conteneurs, images, réseaux, volumes)"
    echo "6) Quitter"
}

# Boucle principale
while true; do
    display_menu
    read -p "Entrez votre choix [1-6]: " choice

    case $choice in
        1)
            echo "Suppression des conteneurs arrêtés..."
            docker container prune -f
            ;;
        2)
            echo "Suppression des images non utilisées..."
            docker image prune -a -f
            ;;
        3)
            echo "Suppression des réseaux non utilisés..."
            docker network prune -f
            ;;
        4)
            echo "Suppression des volumes non utilisés..."
            docker volume prune -f
            ;;
        5)
            echo "Prune complet de l'environnement Docker..."
            docker system prune -a --volumes -f
            ;;
        6)
            echo "Sortie du script."
            exit 0
            ;;
        *)
            echo "Choix invalide. Veuillez réessayer."
            ;;
    esac

    echo "Nettoyage terminé."
    echo ""
done