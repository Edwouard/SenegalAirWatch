# Rapport d’analyse de la pollution de l’air au Sénégal

## Introduction

Ce rapport présente le travail de collecte, traitement et analyse des données relatives à la qualité de l’air provenant de huit stations de mesure réparties au Sénégal.  
Les données ont été extraites via la plateforme OpenAQ, qui fournit des mesures de différents polluants atmosphériques.

L’objectif est de comprendre la répartition spatiale et temporelle des polluants, d’identifier les niveaux moyens de pollution aux différentes stations, et d’effectuer une analyse comparative entre les stations et les polluants mesurés.

---

## 1. Collecte des données

- Données collectées depuis **8 stations** de surveillance de la qualité de l’air au Sénégal.
- Les fichiers CSV de chaque station ont été récupérés et stockés dans un dossier dédié.
- Les données comprennent :
  - Date et heure locale (`datetimeLocal`)
  - Nom de la station (`location_name`)
  - Type de polluant mesuré (`parameter`)
  - Valeur mesurée (`value`)
  - Unité de mesure (`unit`)
  - Latitude et longitude (`latitude`, `longitude`)

### Traitement initial

- Fusion de tous les fichiers CSV en un seul DataFrame global.
- Conversion des dates en format datetime.
- Sélection des colonnes essentielles pour l’analyse.

---

## 2. Visualisation géographique des stations

- Création d’une carte interactive centrée sur Dakar avec la bibliothèque **Folium**.
- Chaque station est représentée par un cercle coloré selon la moyenne de concentration de polluants :
  - Vert : faible pollution (< 10 µg/m³)
  - Orange : pollution modérée (10-20 µg/m³)
  - Rouge : pollution élevée (20-30 µg/m³)
  - Rouge foncé : pollution très élevée (> 30 µg/m³)
  
Cette carte facilite la localisation des zones les plus polluées.

---

## 3. Analyse temporelle

- Visualisation interactive des concentrations des polluants dans le temps avec **Plotly**.
- Série temporelle par polluant, avec possibilité de sélectionner le polluant affiché.
- Permet d’observer les variations et tendances sur la période étudiée.

---

## 4. Analyse comparative entre stations

- Boxplots interactifs pour comparer la distribution des concentrations par station.
- Mise en évidence des disparités entre les stations et identification des zones à risque.
- Boxplots aussi réalisés par polluant pour analyser la qualité de l’air selon la substance mesurée.

---

## 5. Résultats clés

- Variabilité importante des concentrations selon les stations et les polluants.
- Certaines stations affichent régulièrement des niveaux au-dessus des normes recommandées.
- Différences notables dans le comportement temporel des polluants mesurés.

---

## 6. Conclusion

Ce travail a permis de collecter, consolider et analyser les données de pollution atmosphérique au Sénégal.  
Les visualisations et analyses réalisées fournissent une base solide pour la compréhension de la dynamique spatiale et temporelle de la pollution, ainsi que pour la prise de décision en matière de gestion environnementale.


