import requests
import pandas as pd
from datetime import datetime

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

start_date = "2024-01-01"
end_date = datetime.utcnow().date().isoformat()

variables = "temperature_2m,relative_humidity_2m,pressure_msl,windspeed_10m"

all_data = []

print(f"Téléchargement des données du {start_date} au {end_date}...\n")

for station_name, coord in stations.items():
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={coord['lat']}&longitude={coord['lon']}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly={variables}"
        f"&timezone=UTC"
    )
    print(f"Téléchargement pour {station_name}...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "hourly" in data:
            df = pd.DataFrame(data["hourly"])
            df["time"] = pd.to_datetime(df["time"])
            df["station"] = station_name  # Ajouter colonne ici
            all_data.append(df)
            print(f"✅ Données récupérées pour {station_name}")
        else:
            print(f"⚠️  Pas de données horaires pour {station_name}")

    except Exception as e:
        print(f"❌ Erreur pour {station_name} : {e}")

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    print(f"\nColonnes dans le DataFrame final : {final_df.columns.tolist()}")
    final_df.to_csv("stations_meteo_dakar.csv", index=False)
    print("✅ Données sauvegardées dans 'stations_meteo_dakar.csv'")
else:
    print("❌ Aucune donnée n'a pu être récupérée.")
