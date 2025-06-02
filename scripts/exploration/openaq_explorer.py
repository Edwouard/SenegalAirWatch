#!/usr/bin/env python3
"""
Script d'exploration des stations de qualité de l'air au Sénégal via l'API OpenAQ

Ce script identifie toutes les stations de mesure de qualité de l'air au Sénégal,
explore leurs capteurs et exporte les résultats dans des formats exploitables
pour la phase de collecte de données.

Auteur: Équipe SenegalAirWatch
Date: Mai 2025
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configuration du logging pour suivre les opérations avec support Unicode complet
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("exploration_stations.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Configuration spécifique pour Windows - approche plus douce
import sys

if sys.platform.startswith("win"):
    # Sur Windows, on utilise une approche moins invasive pour l'Unicode
    import locale

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except:
            # Si la reconfiguration échoue, on continue sans forcer l'UTF-8
            pass

# Gestion sécurisée des variables d'environnement avec python-dotenv
try:
    from dotenv import load_dotenv

    # Chargement automatique du fichier .env s'il existe
    load_dotenv()
    logger.info("Fichier .env chargé avec succès")
except ImportError:
    logger.warning(
        "Package python-dotenv non installé. Installez-le avec: pip install python-dotenv"
    )
    logger.info("Utilisation des variables d'environnement système uniquement")

# Gestion robuste des imports OpenAQ avec détection automatique de la structure
try:
    from openaq import OpenAQ

    logger.info("Package OpenAQ importé avec succès")

    # Tentative d'import des exceptions avec gestion des différentes structures possibles
    try:
        # Structure moderne (versions récentes)
        from openaq.exceptions import RateLimitError, ServerError, AuthError

        logger.info("Exceptions OpenAQ importées depuis openaq.exceptions")
    except ImportError:
        try:
            # Structure alternative (certaines versions)
            from openaq import RateLimitError, ServerError, AuthError

            logger.info("Exceptions OpenAQ importées depuis le module principal")
        except ImportError:
            # Fallback : utilisation des exceptions HTTP standard
            logger.warning(
                "Exceptions spécifiques OpenAQ non trouvées, utilisation des exceptions standard"
            )

            # Définition d'exceptions de substitution basées sur les exceptions standard
            class RateLimitError(Exception):
                """Exception levée quand la limite de taux API est dépassée"""

                pass

            class ServerError(Exception):
                """Exception levée pour les erreurs serveur (5xx)"""

                pass

            class AuthError(Exception):
                """Exception levée pour les erreurs d'authentification"""

                pass

            logger.info("Exceptions de substitution définies")

except ImportError:
    logger.error(
        "Le package OpenAQ n'est pas installé. Installez-le avec: pip install openaq"
    )
    print("\n❌ PACKAGE MANQUANT")
    print("Le package OpenAQ n'est pas installé sur votre système.")
    print("\nPour l'installer, exécutez cette commande :")
    print("pip install openaq")
    print("\nOu si vous utilisez conda :")
    print("conda install -c conda-forge openaq")
    exit(1)


class ExploratorStationsSenegal:
    """
    Classe principale pour l'exploration des stations de qualité de l'air au Sénégal.

    Cette classe encapsule toute la logique d'exploration, depuis la connexion à l'API
    jusqu'à l'export des résultats. Elle suit une approche méthodique pour garantir
    que nous récupérons toutes les informations nécessaires à la phase de collecte.
    """

    def __init__(self, api_key: str = None):
        """
        Initialise l'explorateur avec la clé API OpenAQ en suivant les bonnes pratiques de sécurité.

        Cette méthode cherche la clé API selon une hiérarchie de priorité :
        1. Paramètre direct (à éviter en production)
        2. Variable d'environnement OPENAQ_API_KEY
        3. Fichier .env dans le répertoire de travail

        Args:
            api_key: Clé API OpenAQ. Si fournie, override les autres sources (non recommandé en production).
        """
        # Priorité 1: Paramètre direct (avec avertissement de sécurité)
        if api_key:
            logger.warning(
                "Clé API fournie directement en paramètre. En production, utilisez plutôt les variables d'environnement."
            )
            self.api_key = api_key
        else:
            # Priorité 2: Variable d'environnement (recommandée)
            self.api_key = os.getenv("OPENAQ_API_KEY")

        # Validation de la présence de la clé API
        if not self.api_key:
            error_message = (
                "Clé API OpenAQ introuvable. Méthodes recommandées :\n"
                "1. Créer un fichier .env avec : OPENAQ_API_KEY=votre_clé\n"
                "2. Définir la variable d'environnement : export OPENAQ_API_KEY=votre_clé\n"
                "3. Obtenir une clé gratuite sur : https://explore.openaq.org/register"
            )
            raise ValueError(error_message)

        self.client = None
        self.stations_data = []
        self.sensors_data = []
        self.exploration_summary = {}

        # Métadonnées pour l'exploration
        self.timestamp_exploration = datetime.now().isoformat()

    def connect_to_api(self) -> bool:
        """
        Établit la connexion avec l'API OpenAQ et teste l'authentification.

        Returns:
            bool: True si la connexion est réussie, False sinon.
        """
        try:
            self.client = OpenAQ(api_key=self.api_key)
            logger.info("Connexion à l'API OpenAQ établie avec succès")
            return True

        except AuthError as e:
            logger.error(f"Erreur d'authentification: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à l'API: {e}")
            return False

    def discover_senegal_stations(self) -> List[Dict[str, Any]]:
        """
        Découvre toutes les stations de mesure au Sénégal.

        Cette méthode utilise le code ISO du Sénégal (SN) pour filtrer les stations.
        Elle récupère également des informations contextuelles importantes comme
        les coordonnées géographiques et les types d'instruments.

        Returns:
            List[Dict]: Liste des stations avec leurs métadonnées complètes.
        """
        logger.info("Début de la découverte des stations sénégalaises...")

        try:
            # Récupération des stations avec le code ISO du Sénégal
            response = self.client.locations.list(
                iso="SN",  # Code ISO du Sénégal
                limit=1000,  # Maximum pour être sûr de tout récupérer
                order_by="id",
                sort_order="asc",
            )

            logger.info(f"Nombre total de stations trouvées: {len(response.results)}")

            for location in response.results:
                # Extraction des informations essentielles de chaque station
                station_info = {
                    "station_id": location.id,
                    "nom": location.name,
                    "localite": location.locality,
                    "pays": location.country.name if location.country else "N/A",
                    "code_pays": location.country.code if location.country else "N/A",
                    "latitude": (
                        location.coordinates.latitude if location.coordinates else None
                    ),
                    "longitude": (
                        location.coordinates.longitude if location.coordinates else None
                    ),
                    "proprietaire": location.owner.name if location.owner else "N/A",
                    "fournisseur": (
                        location.provider.name if location.provider else "N/A"
                    ),
                    "est_mobile": location.is_mobile,
                    "est_moniteur": location.is_monitor,
                    "premiere_mesure": (
                        location.datetime_first.utc if location.datetime_first else None
                    ),
                    "derniere_mesure": (
                        location.datetime_last.utc if location.datetime_last else None
                    ),
                    "nombre_capteurs": len(location.sensors) if location.sensors else 0,
                    "types_instruments": (
                        [instr.name for instr in location.instruments]
                        if location.instruments
                        else []
                    ),
                    "date_exploration": self.timestamp_exploration,
                }

                self.stations_data.append(station_info)

                logger.info(
                    f"Station explorée: {station_info['nom']} (ID: {station_info['station_id']})"
                )

            return self.stations_data

        except RateLimitError:
            logger.warning("Limite de taux atteinte lors de la découverte des stations")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la découverte des stations: {e}")
            raise

    def _safe_get_value(self, obj, attribute_path: str, default="N/A"):
        """
        Méthode utilitaire améliorée pour extraire des valeurs de manière sécurisée depuis des objets
        ou des dictionnaires, avec gestion avancée des structures imbriquées.

        Cette version améliorée peut gérer les objets Python complexes avec des attributs imbriqués,
        ce qui est crucial pour extraire les informations des paramètres OpenAQ.

        Args:
            obj: L'objet ou dictionnaire source
            attribute_path: Chemin vers l'attribut (ex: "parameter.name")
            default: Valeur par défaut si l'attribut n'existe pas

        Returns:
            La valeur extraite ou la valeur par défaut
        """
        try:
            # Diviser le chemin d'attribut (ex: "parameter.name" -> ["parameter", "name"])
            path_parts = attribute_path.split(".")
            current_obj = obj

            for part in path_parts:
                # Tentative d'accès comme attribut d'objet (ex: sensor.id)
                if hasattr(current_obj, part):
                    current_obj = getattr(current_obj, part)
                    # Vérification supplémentaire pour les objets None
                    if current_obj is None:
                        return default
                # Tentative d'accès comme clé de dictionnaire (ex: sensor['id'])
                elif isinstance(current_obj, dict) and part in current_obj:
                    current_obj = current_obj[part]
                    if current_obj is None:
                        return default
                else:
                    # Si aucune méthode ne fonctionne, retourner la valeur par défaut
                    return default

            # Gestion spéciale pour les objets qui peuvent être vides mais valides
            if current_obj == "" or current_obj == 0:
                return current_obj
            elif current_obj is None:
                return default
            else:
                return current_obj

        except Exception as e:
            # Log du problème pour diagnostic sans interrompre le processus
            logger.debug(f"Erreur d'extraction pour {attribute_path}: {e}")
            return default

    def _extract_parameter_info(self, sensor):
        """
        Extraction spécialisée des informations de paramètre basée sur la découverte que
        sensor.parameter est un dictionnaire Python, pas un objet Parameter.

        Cette méthode utilise la structure réelle révélée par notre diagnostic :
        - sensor.parameter est un dictionnaire
        - Les clés du dictionnaire contiennent les informations que nous cherchons

        Args:
            sensor: Objet Sensor d'OpenAQ

        Returns:
            dict: Informations extraites du paramètre ou valeurs par défaut
        """
        param_info = {
            "parametre_id": "N/A",
            "parametre_nom": "N/A",
            "parametre_nom_affichage": "N/A",
            "unite_mesure": "N/A",
        }

        try:
            # Vérification que l'objet sensor a bien un attribut parameter
            if not hasattr(sensor, "parameter"):
                logger.debug("Sensor sans attribut parameter")
                return param_info

            param_dict = sensor.parameter

            # Vérification que l'objet parameter n'est pas None
            if param_dict is None:
                logger.debug("Attribut parameter est None")
                return param_info

            # Maintenant nous savons que parameter est un dictionnaire !
            # Extraction sécurisée de chaque clé du dictionnaire
            if isinstance(param_dict, dict):
                # ID du paramètre
                if "id" in param_dict and param_dict["id"] is not None:
                    param_info["parametre_id"] = param_dict["id"]

                # Nom du paramètre
                if "name" in param_dict and param_dict["name"] is not None:
                    param_info["parametre_nom"] = param_dict["name"]

                # Nom d'affichage
                if (
                    "display_name" in param_dict
                    and param_dict["display_name"] is not None
                ):
                    param_info["parametre_nom_affichage"] = param_dict["display_name"]
                elif param_info["parametre_nom"] != "N/A":
                    # Fallback sur le nom standard si display_name n'est pas disponible
                    param_info["parametre_nom_affichage"] = param_info["parametre_nom"]

                # Unités de mesure
                if "units" in param_dict and param_dict["units"] is not None:
                    param_info["unite_mesure"] = param_dict["units"]

                # Diagnostic pour comprendre les cas où l'extraction échoue encore
                if param_info["parametre_nom"] == "N/A":
                    logger.debug(
                        f"Extraction échouée - Clés disponibles dans le dictionnaire: {list(param_dict.keys())}"
                    )
                    logger.debug(f"Contenu du dictionnaire parameter: {param_dict}")
            else:
                # Si ce n'est pas un dictionnaire, loguer le type pour diagnostic
                logger.debug(
                    f"parameter n'est pas un dictionnaire mais : {type(param_dict)}"
                )
                if hasattr(param_dict, "__dict__"):
                    logger.debug(f"Contenu __dict__: {param_dict.__dict__}")

            return param_info

        except Exception as e:
            logger.debug(f"Erreur lors de l'extraction des paramètres: {e}")
            return param_info

    def explore_station_sensors(
        self, station_id: int, station_name: str
    ) -> List[Dict[str, Any]]:
        """
        Explore en détail tous les capteurs d'une station donnée en utilisant notre
        compréhension corrigée que sensor.parameter est un dictionnaire.

        Cette version utilise une approche d'extraction adaptée à la structure réelle
        révélée par notre diagnostic : les paramètres sont des dictionnaires Python.

        Args:
            station_id: Identifiant unique de la station
            station_name: Nom de la station pour les logs

        Returns:
            List[Dict]: Liste des capteurs avec leurs spécifications complètes.
        """
        logger.info(f"Exploration des capteurs de la station: {station_name}")

        station_sensors = []

        try:
            # Récupération des capteurs de la station
            sensors_response = self.client.locations.sensors(station_id)

            # Diagnostic simplifié maintenant que nous comprenons la structure
            logger.debug(
                f"Nombre de capteurs reçus: {len(sensors_response.results) if hasattr(sensors_response, 'results') else 0}"
            )

            for i, sensor in enumerate(sensors_response.results):
                try:
                    # Extraction des informations de base du capteur
                    sensor_info = {
                        "station_id": station_id,
                        "station_nom": station_name,
                        "capteur_id": self._safe_get_value(sensor, "id"),
                        "capteur_nom": self._safe_get_value(sensor, "name"),
                        "date_exploration": self.timestamp_exploration,
                    }

                    # Extraction spécialisée des informations de paramètre (dictionnaire)
                    param_info = self._extract_parameter_info(sensor)
                    sensor_info.update(param_info)

                    # Validation que nous avons récupéré des données significatives
                    has_valid_data = (
                        sensor_info["capteur_id"] != "N/A"
                        or sensor_info["parametre_nom"] != "N/A"
                        or sensor_info["unite_mesure"] != "N/A"
                    )

                    if has_valid_data:
                        station_sensors.append(sensor_info)
                        self.sensors_data.append(sensor_info)

                        logger.debug(
                            f"  Capteur {i+1}: {sensor_info['parametre_nom_affichage']} ({sensor_info['unite_mesure']})"
                        )
                    else:
                        logger.warning(
                            f"  Capteur {i+1}: Aucune donnée significative extraite"
                        )

                except Exception as sensor_error:
                    logger.warning(
                        f"  Erreur lors du traitement du capteur {i+1}: {sensor_error}"
                    )
                    continue

            logger.info(
                f"  -> {len(station_sensors)} capteurs traités avec succès pour {station_name}"
            )

            return station_sensors

        except Exception as e:
            logger.error(
                f"Erreur lors de l'exploration des capteurs de {station_name}: {e}"
            )
            logger.debug(
                f"Détails de l'erreur pour {station_name}: {type(e).__name__}: {str(e)}"
            )
            return []

    def diagnose_api_response_structure(self, station_id: int, station_name: str):
        """
        Fonction de diagnostic pour comprendre la structure exacte des données
        retournées par l'API OpenAQ pour les capteurs.

        Cette méthode nous aide à comprendre pourquoi nous obtenons des dictionnaires
        au lieu d'objets avec attributs, ce qui est essentiel pour adapter notre code.

        Args:
            station_id: ID de la station à diagnostiquer
            station_name: Nom de la station pour les logs
        """
        logger.info(f"=== DIAGNOSTIC APPROFONDI POUR {station_name} ===")

        try:
            sensors_response = self.client.locations.sensors(station_id)

            # Analyser la structure de la réponse globale
            logger.info(f"Type de réponse: {type(sensors_response)}")
            logger.info(f"Attributs de la réponse: {dir(sensors_response)}")

            if hasattr(sensors_response, "results"):
                logger.info(
                    f"Nombre d'éléments dans results: {len(sensors_response.results)}"
                )

                if sensors_response.results:
                    # Analyser le premier élément en détail
                    first_sensor = sensors_response.results[0]
                    logger.info(f"Type du premier capteur: {type(first_sensor)}")

                    if isinstance(first_sensor, dict):
                        logger.info("✓ Le capteur est un dictionnaire")
                        logger.info(f"Clés disponibles: {list(first_sensor.keys())}")

                        # Examiner la structure imbriquée
                        for key, value in first_sensor.items():
                            logger.info(f"  {key}: {type(value)} = {value}")
                    else:
                        logger.info("✓ Le capteur est un objet")
                        logger.info(f"Attributs disponibles: {dir(first_sensor)}")

                # Examiner aussi les métadonnées de la réponse si disponibles
                if hasattr(sensors_response, "meta"):
                    logger.info(f"Métadonnées disponibles: {sensors_response.meta}")

        except Exception as e:
            logger.error(f"Erreur lors du diagnostic: {e}")

        logger.info("=== FIN DU DIAGNOSTIC ===")

    def run_complete_exploration(self):
        """
        Exécute l'exploration complète de toutes les stations sénégalaises avec diagnostic intégré.

        Cette version améliorée inclut un diagnostic automatique de la structure des données
        pour la première station, ce qui nous aide à comprendre et adapter notre approche.
        """
        logger.info("=== DÉBUT DE L'EXPLORATION COMPLÈTE ===")

        # Étape 1: Connexion à l'API
        if not self.connect_to_api():
            raise ConnectionError("Impossible de se connecter à l'API OpenAQ")

        try:
            # Étape 2: Découverte des stations
            stations = self.discover_senegal_stations()

            # Étape 3: Diagnostic sur la première station pour comprendre la structure
            if stations:
                logger.info("=== DIAGNOSTIC DE LA STRUCTURE API ===")
                self.diagnose_api_response_structure(
                    stations[0]["station_id"], stations[0]["nom"]
                )

            # Étape 4: Exploration détaillée de chaque station
            logger.info("Début de l'exploration détaillée des capteurs...")

            total_sensors = 0
            stations_avec_donnees = 0

            for station in stations:
                station_sensors = self.explore_station_sensors(
                    station["station_id"], station["nom"]
                )

                if station_sensors:
                    stations_avec_donnees += 1
                    total_sensors += len(station_sensors)

            # Compilation du résumé d'exploration
            self.exploration_summary = {
                "timestamp_exploration": self.timestamp_exploration,
                "nombre_total_stations": len(stations),
                "stations_avec_capteurs": stations_avec_donnees,
                "nombre_total_capteurs": total_sensors,
                "parametres_uniques": self._get_unique_parameters(),
                "repartition_geographique": self._analyze_geographic_distribution(),
                "periode_donnees": self._analyze_data_timespan(),
                "statut_exploration": "SUCCÈS",
            }

            logger.info("=== EXPLORATION TERMINÉE AVEC SUCCÈS ===")
            logger.info(f"Stations trouvées: {len(stations)}")
            logger.info(f"Capteurs totaux: {total_sensors}")
            logger.info(
                f"Paramètres uniques: {len(self.exploration_summary['parametres_uniques'])}"
            )

        except Exception as e:
            logger.error(f"Erreur durant l'exploration: {e}")
            self.exploration_summary["statut_exploration"] = f"ERREUR: {str(e)}"
            raise

        finally:
            # Fermeture propre de la connexion API
            if self.client:
                self.client.close()
                logger.info("Connexion API fermée")

    def _get_unique_parameters(self) -> List[Dict[str, str]]:
        """Analyse les paramètres uniques mesurés across toutes les stations."""
        parametres_uniques = {}

        for sensor in self.sensors_data:
            param_key = sensor["parametre_nom"]
            if param_key not in parametres_uniques:
                parametres_uniques[param_key] = {
                    "nom": sensor["parametre_nom"],
                    "nom_affichage": sensor["parametre_nom_affichage"],
                    "unite": sensor["unite_mesure"],
                    "nombre_capteurs": 0,
                }
            parametres_uniques[param_key]["nombre_capteurs"] += 1

        return list(parametres_uniques.values())

    def _analyze_geographic_distribution(self) -> Dict[str, Any]:
        """Analyse la répartition géographique des stations."""
        localites = {}
        coordonnees_valides = 0

        for station in self.stations_data:
            localite = station["localite"] or "Non spécifiée"
            localites[localite] = localites.get(localite, 0) + 1

            if station["latitude"] and station["longitude"]:
                coordonnees_valides += 1

        return {
            "repartition_par_localite": localites,
            "stations_avec_coordonnees": coordonnees_valides,
            "pourcentage_geolocalise": (
                round((coordonnees_valides / len(self.stations_data)) * 100, 2)
                if self.stations_data
                else 0
            ),
        }

    def _analyze_data_timespan(self) -> Dict[str, Any]:
        """Analyse la période temporelle couverte par les données."""
        premieres_mesures = [
            s["premiere_mesure"] for s in self.stations_data if s["premiere_mesure"]
        ]
        dernieres_mesures = [
            s["derniere_mesure"] for s in self.stations_data if s["derniere_mesure"]
        ]

        if not premieres_mesures or not dernieres_mesures:
            return {"statut": "Pas de données temporelles disponibles"}

        return {
            "premiere_mesure_globale": min(premieres_mesures),
            "derniere_mesure_globale": max(dernieres_mesures),
            "stations_avec_donnees_temporelles": len(premieres_mesures),
        }

    def export_results(self, base_filename: str = "exploration_stations_senegal"):
        """
        Exporte les résultats d'exploration dans plusieurs formats pour faciliter l'analyse.

        Cette méthode crée plusieurs fichiers complémentaires :
        - Un fichier JSON complet avec toutes les données brutes
        - Des fichiers CSV structurés pour l'analyse dans Excel ou autres outils
        - Un rapport de synthèse lisible par l'humain

        Args:
            base_filename: Nom de base pour les fichiers d'export
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export JSON complet (données brutes pour usage programmatique)
        json_filename = f"{base_filename}_{timestamp}.json"
        export_data = {
            "metadata": {
                "timestamp_exploration": self.timestamp_exploration,
                "timestamp_export": datetime.now().isoformat(),
                "version_script": "1.0",
                "description": "Exploration complète des stations OpenAQ au Sénégal",
            },
            "summary": self.exploration_summary,
            "stations": self.stations_data,
            "sensors": self.sensors_data,
        }

        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Données complètes exportées vers: {json_filename}")

        # Export CSV des stations (pour analyse tabulaire)
        stations_csv = f"{base_filename}_stations_{timestamp}.csv"
        df_stations = pd.DataFrame(self.stations_data)
        df_stations.to_csv(stations_csv, index=False, encoding="utf-8")
        logger.info(f"Données des stations exportées vers: {stations_csv}")

        # Export CSV des capteurs (pour analyse détaillée)
        sensors_csv = f"{base_filename}_capteurs_{timestamp}.csv"
        df_sensors = pd.DataFrame(self.sensors_data)
        df_sensors.to_csv(sensors_csv, index=False, encoding="utf-8")
        logger.info(f"Données des capteurs exportées vers: {sensors_csv}")

        # Rapport de synthèse (format texte lisible)
        rapport_filename = f"{base_filename}_rapport_{timestamp}.txt"
        self._generate_synthesis_report(rapport_filename)

        logger.info("=== EXPORT TERMINÉ ===")
        logger.info(f"Fichiers générés:")
        logger.info(f"  - {json_filename} (données complètes)")
        logger.info(f"  - {stations_csv} (stations)")
        logger.info(f"  - {sensors_csv} (capteurs)")
        logger.info(f"  - {rapport_filename} (rapport de synthèse)")

    def _generate_synthesis_report(self, filename: str):
        """Génère un rapport de synthèse lisible par l'humain."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                "RAPPORT DE SYNTHÈSE - EXPLORATION DES STATIONS OPENAQ AU SÉNÉGAL\n"
            )
            f.write("=" * 70 + "\n\n")

            f.write(f"Date d'exploration: {self.timestamp_exploration}\n")
            f.write(
                f"Statut: {self.exploration_summary.get('statut_exploration', 'N/A')}\n\n"
            )

            # Statistiques générales
            f.write("STATISTIQUES GÉNÉRALES\n")
            f.write("-" * 30 + "\n")
            f.write(
                f"Nombre total de stations: {self.exploration_summary.get('nombre_total_stations', 0)}\n"
            )
            f.write(
                f"Stations avec capteurs: {self.exploration_summary.get('stations_avec_capteurs', 0)}\n"
            )
            f.write(
                f"Nombre total de capteurs: {self.exploration_summary.get('nombre_total_capteurs', 0)}\n"
            )
            f.write(
                f"Paramètres uniques mesurés: {len(self.exploration_summary.get('parametres_uniques', []))}\n\n"
            )

            # Répartition géographique
            repartition = self.exploration_summary.get("repartition_geographique", {})
            f.write("RÉPARTITION GÉOGRAPHIQUE\n")
            f.write("-" * 30 + "\n")
            for localite, count in repartition.get(
                "repartition_par_localite", {}
            ).items():
                f.write(f"  {localite}: {count} station(s)\n")
            f.write(
                f"\nStations géolocalisées: {repartition.get('pourcentage_geolocalise', 0)}%\n\n"
            )

            # Paramètres mesurés
            f.write("PARAMÈTRES MESURÉS\n")
            f.write("-" * 30 + "\n")
            for param in self.exploration_summary.get("parametres_uniques", []):
                f.write(
                    f"  {param['nom_affichage']} ({param['unite']}) - {param['nombre_capteurs']} capteur(s)\n"
                )

            # Recommandations pour la collecte
            f.write("\n\nRECOMMANDATIONS POUR LA COLLECTE DE DONNÉES\n")
            f.write("-" * 50 + "\n")
            f.write(
                "1. Prioriser les paramètres PM1, PM2.5 et PM10 (particules fines)\n"
            )
            f.write("2. Inclure les données météorologiques (température, humidité)\n")
            f.write("3. Considérer la fréquence de collecte selon l'usage prévu\n")
            f.write("4. Planifier la gestion des données manquantes\n")
            f.write("5. Tester la collecte sur une station avant déploiement complet\n")


def main():
    """
    Fonction principale qui orchestre l'exploration complète.

    Cette fonction suit les meilleures pratiques de sécurité en gérant les clés API
    via des variables d'environnement plutôt que par saisie interactive.
    """
    print("=== EXPLORATEUR DES STATIONS OPENAQ AU SÉNÉGAL ===\n")

    # Vérification et guidance pour la configuration de la clé API
    api_key = os.getenv("OPENAQ_API_KEY")
    if not api_key:
        print("❌ CONFIGURATION REQUISE - Clé API OpenAQ manquante")
        print(
            "\nPour configurer votre clé API de manière sécurisée, suivez ces étapes :"
        )
        print("\n📝 MÉTHODE RECOMMANDÉE (fichier .env) :")
        print("   1. Créez un fichier nommé '.env' dans ce répertoire")
        print("   2. Ajoutez cette ligne : OPENAQ_API_KEY=votre_clé_api_ici")
        print("   3. Relancez le script")
        print("\n🔐 MÉTHODE ALTERNATIVE (variable d'environnement) :")
        print("   Linux/Mac: export OPENAQ_API_KEY=votre_clé_api_ici")
        print("   Windows: set OPENAQ_API_KEY=votre_clé_api_ici")
        print("\n🌐 Obtenir une clé API gratuite :")
        print("   https://explore.openaq.org/register")
        print(
            "\n⚠️  IMPORTANT : Ne jamais inclure votre clé API directement dans le code source"
        )

        # Proposer une aide immédiate pour créer le fichier .env
        response = (
            input(
                "\nVoulez-vous que je vous aide à créer le fichier .env maintenant ? (o/n): "
            )
            .strip()
            .lower()
        )
        if response in ["o", "oui", "y", "yes"]:
            create_env_file_interactively()
        else:
            print("\nConfigurez votre clé API puis relancez le script.")
            return
    else:
        print("✅ Clé API OpenAQ détectée")

    try:
        # Initialisation et exécution de l'exploration
        explorer = ExploratorStationsSenegal()  # Plus besoin de passer la clé API
        explorer.run_complete_exploration()

        # Export des résultats
        print("\nExport des résultats en cours...")
        explorer.export_results()

        print("\n🎉 Exploration terminée avec succès!")
        print("\nProchaines étapes recommandées:")
        print("1. Examiner les fichiers CSV générés")
        print("2. Analyser le rapport de synthèse")
        print("3. Identifier les stations et paramètres prioritaires")
        print("4. Planifier la stratégie de collecte de données")

    except KeyboardInterrupt:
        print("\nExploration interrompue par l'utilisateur.")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        print(f"\n❌ Erreur durant l'exploration: {e}")
        print("Consultez le fichier exploration_stations.log pour plus de détails.")


def create_env_file_interactively():
    """
    Aide l'utilisateur à créer un fichier .env de manière sécurisée.

    Cette fonction guide l'utilisateur dans la création d'un fichier .env
    en validant la clé API et en créant le fichier avec les bonnes permissions.
    """
    print("\n=== CRÉATION DU FICHIER .env ===")

    # Vérification si le fichier .env existe déjà
    if os.path.exists(".env"):
        print("⚠️  Un fichier .env existe déjà dans ce répertoire.")
        overwrite = input("Voulez-vous le remplacer ? (o/n): ").strip().lower()
        if overwrite not in ["o", "oui", "y", "yes"]:
            print("Opération annulée. Vérifiez votre fichier .env existant.")
            return

    # Saisie sécurisée de la clé API
    print("\n📋 Saisissez votre clé API OpenAQ :")
    print("   (La saisie sera masquée pour des raisons de sécurité)")

    try:
        import getpass

        api_key = getpass.getpass("Clé API: ").strip()
    except ImportError:
        # Fallback si getpass n'est pas disponible
        print("⚠️  Module getpass non disponible, saisie visible :")
        api_key = input("Clé API: ").strip()

    if not api_key:
        print("❌ Clé API vide. Opération annulée.")
        return

    # Validation basique du format de la clé
    if len(api_key) < 10:  # Les clés API OpenAQ sont généralement plus longues
        print("⚠️  Cette clé semble trop courte. Vérifiez qu'elle soit complète.")
        continue_anyway = input("Continuer quand même ? (o/n): ").strip().lower()
        if continue_anyway not in ["o", "oui", "y", "yes"]:
            print("Opération annulée.")
            return

    # Création du fichier .env
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"# Configuration pour l'exploration des stations OpenAQ\n")
            f.write(
                f"# Fichier généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"OPENAQ_API_KEY={api_key}\n")

        # Définir les permissions restrictives sur le fichier .env (Unix/Linux/Mac)
        try:
            import stat

            os.chmod(
                ".env", stat.S_IRUSR | stat.S_IWUSR
            )  # Lecture/écriture pour le propriétaire uniquement
            print("🔒 Permissions restrictives appliquées au fichier .env")
        except:
            print(
                "⚠️  Impossible de modifier les permissions du fichier (normal sous Windows)"
            )

        print("✅ Fichier .env créé avec succès!")
        print("\n🔒 RAPPELS DE SÉCURITÉ :")
        print("   - Ne partagez jamais votre fichier .env")
        print("   - Ajoutez '.env' à votre fichier .gitignore")
        print("   - Ne committez jamais ce fichier dans votre dépôt Git")

        # Vérification que le fichier .env est dans .gitignore
        gitignore_reminder()

    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}")


def gitignore_reminder():
    """
    Rappelle l'importance d'ajouter .env au .gitignore et propose de le faire automatiquement.
    """
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r", encoding="utf-8") as f:
            gitignore_content = f.read()

        if ".env" not in gitignore_content:
            print("\n📝 SÉCURITÉ GIT : Le fichier .env n'est pas dans votre .gitignore")
            add_to_gitignore = (
                input("Voulez-vous l'ajouter automatiquement ? (o/n): ").strip().lower()
            )
            if add_to_gitignore in ["o", "oui", "y", "yes"]:
                try:
                    with open(".gitignore", "a", encoding="utf-8") as f:
                        f.write("\n# Variables d'environnement sensibles\n.env\n")
                    print("✅ .env ajouté au .gitignore")
                except Exception as e:
                    print(f"❌ Erreur lors de la modification de .gitignore: {e}")
            else:
                print(
                    "⚠️  N'oubliez pas d'ajouter '.env' à votre .gitignore manuellement"
                )
        else:
            print("✅ .env est déjà protégé par .gitignore")
    else:
        print("\n📝 RECOMMANDATION : Créez un fichier .gitignore contenant '.env'")


if __name__ == "__main__":
    main()
