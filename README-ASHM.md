📄 Rapport : Téléchargement et sauvegarde des données météorologiques pour les 8 stations.

Auteur : Alglege SOUENI HOUMBA MABOUNGOU (ASHM)
Projet : Prédiction de la qualité de l'air à Dakar
Tâche : Collecte des données météorologiques
Date : 26 mai 2025

🎯 Objectif de la tâche
Collecter des données météorologiques pour les 8 stations utiles à la prédiction de la qualité de l’air, en complément des données de pollution.


📝 Description
Ce script Python permet de télécharger des données météorologiques horaires depuis l’API Open-Meteo pour plusieurs localisations au Sénégal. Les stations sélectionnées incluent Dakar, Ouakam, Diourbel1, Notre_dameDiourbel2, Saint-Louis, Richard-Toll, Pikine, et Thiès. Les données sont extraites sur la période du 1er janvier 2024 à aujourd’hui.

🔍 Fonctionnalités
✅ Téléchargement automatique des variables météo suivantes :

🌡️ Température à 2 mètres (temperature_2m)

💧 Humidité relative à 2 mètres (relative_humidity_2m)

📈 Pression atmosphérique au niveau de la mer (pressure_msl)

🌬️ Vitesse du vent à 10 mètres (windspeed_10m)

✅ Génération d’un fichier CSV distinct pour chaque station, nommé sous la forme :

php-template
Copier
Modifier
<nom_de_la_station>_meteo.csv
✅ Affichage dans le terminal :

Période de téléchargement

Station en cours de traitement et URL d’appel à l’API

Code de réponse HTTP pour vérifier le succès ou l’échec

Message indiquant si les données ont bien été sauvegardées ou s’il y a eu une erreur

🔧 Technologies utilisées
Python

Bibliothèques : requests, pandas, datetime

🛠️ Mode de fonctionnement
🔸 Pour chaque station, le script :
1️⃣ Construit l’URL d’appel à l’API Open-Meteo avec les coordonnées géographiques et les variables météo demandées.
2️⃣ Envoie une requête GET à l’API.
3️⃣ Vérifie le code de réponse et s’assure que le contenu contient des données horaires (hourly).
4️⃣ Transforme les données en un DataFrame pandas et convertit la colonne time en format datetime.
5️⃣ Exporte les données en un fichier CSV pour cette station.
6️⃣ Affiche un message récapitulatif dans le terminal.


🚀 Exécution
Pour exécuter ce script :

bash
Copier
Modifier
python meteo_download.py
Les fichiers CSV seront générés dans le répertoire courant.



🗂 Dossier concerné
Les données météo sont stockées dansle dossier :

data/

🌐 Source des données
Les données ont été récupérées à l’aide de l’API Open-Meteo, qui permet d'obtenir des données historiques par coordonnées géographiques.

📄 Format des données collectées

Les fichiers sont au format CSV

Chaque ligne représente une mesure horaire.

✅ Étapes réalisées

📁 Création de la structure de dossiers du projets,pour accueillir les données météo.


💾 Creation et sauvegarde des données au format .csv dans le dossier data/.

💾 Creation et sauvegarder des scripts python dans le dossier 
sript/.
💾 Creation et sauvegarder du code de traitement ou d'analyse  dans le dossier notebook/.
💾 Creation et sauvegarder du README-ASHM pour documenter ce travail.



Analyse exploratoire et création de features.