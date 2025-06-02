import requests
import pandas as pd
from datetime import datetime, timedelta

# Dictionnaire des stations avec leurs coordonnées
stations = {
    "Dakar": {"lat": 14.746475571894893, "lon": -17.510440956465402},
    "Ouakam": {"lat": 14.720079659709183, "lon": -17.490598679618262},
    "Diourbel1": {"lat": 14.661614, "lon": -16.23111},
    "Notre_dame_Diourbel2": {"lat": 14.653855, "lon": -16.2306},
    "SaintLouis": {"lat": 16.019319341426606, "lon": -16.490593389948394},
    "RichardToll": {"lat": 16.457985152738317, "lon": -15.705461444809703},
    "Pikine": {"lat": 14.7444588, "lon": -17.4017114},
    "Thies": {"lat": 14.794498116325476, "lon": -16.96105368259619},
}

# Dates : début au 1er janvier 2024, fin aujourd'hui
start_date = "2024-01-01"
end_date = datetime.utcnow().date().isoformat()

print(f"Téléchargement des données du {start_date} au {end_date}")

# Variables météo horaires demandées
variables = "temperature_2m,relative_humidity_2m,pressure_msl,windspeed_10m"

for nom, coord in stations.items():
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={coord['lat']}&longitude={coord['lon']}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly={variables}"
        f"&timezone=UTC"
    )

    print(f"\nTéléchargement des données pour {nom}...")
    print(f"URL: {url}")
    response = requests.get(url)

    # Ajout des impressions pour le debug
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        data = response.json()

        # Vérifier si les données contiennent bien "hourly"
        if "hourly" in data:
            df = pd.DataFrame(data["hourly"])
            df["time"] = pd.to_datetime(df["time"])

            # Sauvegarder en CSV
            filename = f"{nom}_meteo.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Données sauvegardées dans {filename}")
        else:
            print(f"❌ Pas de données 'hourly' pour {nom}")
    else:
        print(
            f"❌ Erreur pour {nom} : {response.status_code} - {response.text}")
