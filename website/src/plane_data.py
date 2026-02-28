from config import MapBounds

from src import app, db
from src.models import PlaneData
from datetime import datetime

import requests

# Using OpenSky REST API
def opensky_fetch_plane_data(area: str):
  with app.app_context():
    print(f"{datetime.now()} | Fetching plane data in {area} area")
    base_url = "https://opensky-network.org/api"
    bound_data = MapBounds[area]

    # Boundary coordinates are defined in MapBounds
    request_url = f"{base_url}/states/all"
    response = requests.get(request_url, params=bound_data)

    # Only handles 200 OK
    if response.status_code == 200:
        plane_data = response.json()
        time_fetched = plane_data["time"]

        print(f"{datetime.now()} | Inserting plane data in {area} area to database")
        
        for data in plane_data["states"]:
            plane_db = PlaneData(
                time_fetched=time_fetched,
                icao24=data[0],
                callsign=data[1],
                origin_country=data[2],
                time_position=data[3],
                last_contact=data[4],
                longitude=data[5],
                latitude=data[6],
                baro_altitude=data[7],
                on_ground=data[8],
                velocity=data[9],
                true_track=data[10],
                vertical_rate=data[11],
                sensors=data[12],
                geo_altitude=data[13],
                squawk=data[14],
                spi=data[15],
                position_source=data[16]
            )
            try:
                db.session.add(plane_db)
                db.session.commit()
            except Exception as e:
                # Rollback changes of database
                db.session.rollback()
                print(f"DB ERROR: {e}")

        print(f"{datetime.now()} | Successfully fetched and inserted {len(plane_data["states"])} plane data")

    else:
        print(f"Failed to retrieve data, {response.status_code}")


