import json

from src import app, db, redis_cache
from src.models import Plane, PlaneData
from .token_manager import OpenSkyTokenManager

from config import Config
from datetime import datetime

import requests

def opensky_fetch_plane_data(area: str, token: OpenSkyTokenManager):
    with app.app_context():
        print(f"{datetime.now()} | Fetching plane data in {area} area")
        request_url = f"{Config.OPENSKY_API_URL}/states/all"
        response = requests.get(
                    request_url, 
                    params=Config.MapBounds[area],
                    headers=token.headers()
                    )
        
        # Only handles 200 OK
        if response.status_code == 200:
            plane_data = response.json()
            # Cache data for future use. Wrapped in try-except to prevent crashes if Redis is dead
            try:
                redis_cache.json().set("latest_plane_data", "$" ,plane_data["states"])
                redis_cache.expire("latest_plane_data", Config.API_FETCH_INTERVAL)
            except Exception as e:
                print(f"Redis cache warning: {e}")
            
            time_fetched = plane_data["time"]
            print(f"{datetime.now()} | Inserting plane data in {area} area to database")
            
            states = plane_data.get("states") or []
            if not states:
                print(f"No planes found in {area} at this time")
            
            for data in states:
                plane_db = db.session.query(Plane).filter_by(icao24=data[0]).first()
                
                if not plane_db :                
                    plane_db = Plane(
                        icao24=data[0],
                        callsign=data[1],
                        origin_country=data[2],
                    )
                    db.session.add(plane_db)
                
                plane_data_db = PlaneData(
                    time_fetched=time_fetched,
                    plane_icao24=data[0],
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
                    position_source=data[16],
                )
                
                plane_db.plane_data.add(plane_data_db)
                db.session.add(plane_data_db)
                
            try:
                db.session.commit()
            except Exception as e:
                # Rollback changes of database
                db.session.rollback()
                print(f"DB ERROR During insert: {e}")
                return None, None
                        
            print(f"{datetime.now()} | Successfully fetched and inserted {len(plane_data["states"])} plane data")
            
            return time_fetched, plane_data["states"]
        else:
            print(f"Failed to retrieve data, {response.status_code}")
            return None, None