# Documentation API OpenAQ - Projet SenegalAirWatch

## Vue d'ensemble du projet

Le projet SenegalAirWatch vise à développer un système de prédiction de la qualité de l'air pour la région de Dakar au Sénégal. Cette documentation présente les résultats de l'exploration de l'infrastructure de surveillance de la qualité de l'air disponible via l'API OpenAQ et les outils développés pour cette exploration.

### Infrastructure découverte

Notre exploration a révélé une infrastructure au Sénégal composée de 8 stations de mesure réparties sur le territoire national. Ces stations utilisent toutes la technologie AirGradient et fournissent des données de qualité professionnelle à travers la plateforme OpenAQ.

## Comprendre l'API OpenAQ

### Architecture générale

L'API OpenAQ suit une structure hiérarchique logique qui reflète l'organisation physique des réseaux de surveillance de la qualité de l'air. Cette hiérarchie comprend quatre niveaux principaux : les pays, les stations (appelées "locations"), les capteurs ("sensors"), et les mesures ("measurements").

Chaque niveau possède un identifiant unique qui permet de naviguer vers les niveaux inférieurs. Cette structure permet une exploration systématique des données disponibles, depuis une vue d'ensemble nationale jusqu'aux mesures individuelles de chaque capteur.

### Structure des données

L'API utilise le SDK Python OpenAQ qui désérialise les réponses JSON en objets Python structurés. Cependant, notre exploration a révélé une particularité importante : les objets Parameter contenus dans les objets Sensor sont en réalité des dictionnaires Python plutôt que des objets avec des attributs. Cette découverte a nécessité une approche d'extraction adaptative pour accéder correctement aux métadonnées des paramètres mesurés.

### Authentification et accès

L'API OpenAQ nécessite une clé d'authentification gratuite obtenue via inscription sur explore.openaq.org/register. Cette clé doit être gérée de manière sécurisée en utilisant des variables d'environnement ou des fichiers de configuration local (.env) plutôt que d'être incluse directement dans le code source.

## Architecture du script d'exploration

### Conception modulaire

Le script d'exploration a été conçu selon une architecture modulaire qui sépare clairement les responsabilités. La classe principale `ExploratorStationsSenegal` orchestre l'ensemble du processus d'exploration en coordonnant différentes phases spécialisées.

Cette approche modulaire facilite la maintenance, les tests, et l'extension future du code. Chaque méthode a une responsabilité spécifique et peut être testée ou modifiée indépendamment des autres composants.

### Gestion robuste des erreurs

Le script implémente une stratégie de gestion d'erreurs à plusieurs niveaux qui garantit la résilience face aux variations de l'API et aux problèmes réseau. Cette stratégie inclut des mécanismes de fallback pour les différentes structures de données possibles et une continuité de service même en cas d'échec partiel.

### Méthode d'extraction adaptative

La méthode `_extract_parameter_info` constitue le cœur technique du script. Cette méthode a été développée pour gérer la structure réelle des données de l'API, où les paramètres sont stockés sous forme de dictionnaires. Elle utilise une approche défensive qui teste d'abord l'existence des clés avant d'accéder aux valeurs, garantissant ainsi une extraction fiable même en cas de variations dans la structure des données.

### Système de diagnostic intégré

Le script inclut un système de diagnostic sophistiqué qui analyse la structure des données retournées par l'API. Ce système nous a permis de découvrir et de corriger la différence entre la documentation officielle et la structure réelle des données. Il constitue un outil précieux pour le débogage et l'adaptation future du code.

## Résultats de l'exploration

### Couverture géographique

L'exploration a identifié 8 stations réparties dans 6 villes du Sénégal, offrant une couverture géographique remarquable. La région de Dakar dispose de 2 stations (Dakar centre et Ouakam), Pikine possède une station de référence, et les autres stations sont situées à Diourbel (2 stations), Saint-Louis, Richard-Toll, et Thiès.

Cette répartition offre une excellente opportunité d'étudier les gradients de pollution urbain-rural et de développer des modèles prédictifs qui capturent les spécificités de différents environnements sénégalais.

### Paramètres mesurés

Toutes les stations mesurent un ensemble cohérent de paramètres essentiels pour la surveillance de la qualité de l'air et la modélisation prédictive. Ces paramètres incluent les particules fines (PM1, PM2.5, et PM10 pour certaines stations), les conditions météorologiques (température et humidité relative), et les comptages de particules ultrafines (um003).

Cette combinaison de données de pollution et de paramètres météorologiques est idéale pour développer des modèles prédictifs robustes, car elle permet de capturer à la fois les sources directes de pollution et les facteurs environnementaux qui influencent la dispersion et la transformation des polluants.

### Période de données disponibles

Les données s'étendent de septembre 2023 à mai 2025, avec la plupart des stations nouvelles commençant leurs mesures en février 2025. Cette couverture temporelle permet d'analyser les variations saisonnières, particulièrement importantes dans le contexte sénégalais où la pollution atmosphérique présente des cycles marqués liés à l'Harmattan et à la saison des pluies.

### Qualité et fiabilité des données

L'infrastructure utilise exclusivement des capteurs AirGradient, garantissant une cohérence technique et une qualité de mesure uniforme sur l'ensemble du réseau. Cette standardisation facilite la comparaison entre stations et améliore la fiabilité des analyses inter-sites.

## Architecture technique pour l'utilisation

### Configuration de l'environnement

Le script nécessite Python 3.9 ou plus récent avec les packages openaq et python-dotenv. La configuration sécurisée des clés API est gérée via un fichier .env qui doit contenir la variable OPENAQ_API_KEY avec votre clé d'authentification.

### Structure des fichiers exportés

Le script génère automatiquement quatre types de fichiers complémentaires pour faciliter l'analyse des résultats. Le fichier JSON contient l'intégralité des données structurées pour un traitement programmatique. Les fichiers CSV fournissent des vues tabulaires des stations et des capteurs pour l'analyse dans Excel ou d'autres outils. Le rapport de synthèse offre une vue d'ensemble lisible par l'humain avec des recommandations pour la suite du projet.

### Extensibilité et adaptation

Le code a été conçu pour faciliter l'extension future vers d'autres pays ou régions. La structure modulaire permet d'adapter facilement les filtres géographiques et d'ajouter de nouvelles fonctionnalités d'analyse sans modification majeure de l'architecture existante.

## Recommandations pour la collecte de données

### Stratégie de priorisation

Basé sur les résultats de l'exploration, nous recommandons une approche de collecte stratifiée qui priorise les stations de la région métropolitaine de Dakar pour la modélisation prédictive locale, tout en incluant les autres stations pour enrichir la compréhension des facteurs régionaux et saisonniers.

Les paramètres PM1, PM2.5 et PM10 doivent être prioritaires car ils représentent les polluants les plus critiques pour la santé publique et sont mesurés de manière cohérente sur l'ensemble du réseau. Les données météorologiques (température et humidité) doivent être systématiquement collectées car elles sont essentielles pour la modélisation prédictive.

### Considérations techniques

La volumétrie des données nécessite une planification appropriée de l'infrastructure de stockage et de traitement. Avec 42 capteurs générant des données potentiellement horaires, le système doit être dimensionné pour gérer environ 367 000 points de données par an.

La gestion des données manquantes doit être planifiée dès le début, car les réseaux de capteurs environnementaux présentent inévitablement des interruptions dues à la maintenance, aux pannes, ou aux conditions météorologiques extrêmes.

## Prochaines étapes recommandées

### Phase de validation

Avant de déployer une collecte de données à grande échelle, nous recommandons de réaliser une phase de validation sur une période courte (7 à 14 jours) pour caractériser la fréquence de mesure, identifier les patterns de données manquantes, et valider la qualité des données collectées.

### Développement du système de collecte

Le script d'exploration fournit les bases techniques pour développer un système de collecte automatisé. Ce système devra inclure des mécanismes de surveillance de la santé des données, des alertes en cas de problème, et une capacité de récupération automatique après les interruptions.

### Architecture de données

La conception de l'architecture de stockage doit prendre en compte la nature temporelle des données et les besoins d'analyse prédictive. Une base de données temporelle ou une structure de fichiers partitionnée par date optimisera les performances pour les requêtes d'analyse statistique et de machine learning.

## Conclusion

L'exploration de l'infrastructure OpenAQ au Sénégal a révélé un écosystème de surveillance de la qualité de l'air remarquablement développé et bien adapté aux besoins du projet SenegalAirWatch. La combinaison de capteurs standardisés, de couverture géographique stratégique, et de paramètres pertinents pour la modélisation prédictive offre une base solide pour développer un système de prédiction de la qualité de l'air efficace pour le Sénégal.

Le script d'exploration développé fournit non seulement les données nécessaires pour planifier la stratégie de collecte, mais établit également les fondations techniques pour les phases suivantes du projet. Son architecture robuste et adaptative garantit qu'il pourra évoluer avec les besoins futurs du projet et s'adapter aux changements potentiels de l'API OpenAQ.

Cette documentation servira de référence technique pour l'équipe et facilitera l'intégration de nouveaux membres au projet en leur fournissant une compréhension complète de l'infrastructure disponible et des outils développés pour l'exploiter.