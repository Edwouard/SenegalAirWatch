Rapport – Collecte des données météorologiques

Auteur : Alglege SOUENI HOUMBA MABOUNGOU (ASHM)
Projet : Prédiction de la qualité de l'air à Dakar
Tâche : Collecte des données météorologiques
Date : 26 mai 2025

🎯 Objectif de la tâche
Collecter des données météorologiques pour les 8 stations utiles à la prédiction de la qualité de l’air, en complément des données de pollution.

🗂 Dossier concerné
Les données météo sont stockées dansle dossier :

data/

🌐 Source des données
Les données ont été récupérées à l’aide de l’API Open-Meteo, qui permet d'obtenir des données historiques par coordonnées géographiques.

📄 Format des données collectées

Les fichiers sont au format CSV, contenant les colonnes suivantes :

time,temperature_2m,relative_humidity_2m,pressure_msl,windspeed_10m


Chaque ligne représente une mesure horaire.

✅ Étapes réalisées

📁 Création de la structure de dossiers du projets,pour accueillir les données météo.

🌐 Utilisation de l'API Open-Meteo pour récupérer les données historiques.

💾 Creation et sauvegarde des données au format .csv dans le dossier data/.

💾 Creation et sauvegarder des scripts python dans le dossier 
sript/.
💾 Creation et sauvegarder du code de traitement ou d'analyse  dans le dossier notebook/.
💾 Creation et sauvegarder du README-ASHM pour documenter ce travail.



Analyse exploratoire et création de features.