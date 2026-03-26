import json

from src import Config, socketio, redis_cache, token 
from src.opensky.helper import opensky_fetch_plane_data

# Function used to fetch new data
def opensky_broadcast_plane_data():
    opensky_fetch_plane_data(Config.SELECTED_MAP_BOUNDS, token)
    try: 
        latest_plane_data = redis_cache.json().get("latest_plane_data")
        if latest_plane_data:
            socketio.emit("latest_data", latest_plane_data)
    except Exception as e:
        print(f"ERROR While getting the latest data: {e}")
            
@socketio.on('connect')
def handle_message():
    print(f'Connect : User connected, sending latest data')
    latest_plane_data = redis_cache.json().get("latest_plane_data")

    # Attempt to fetch new data
    if not latest_plane_data:
        print("Connect : Cache not found, fetch the data")
        opensky_fetch_plane_data(Config.SELECTED_MAP_BOUNDS, token)
        latest_plane_data = latest_plane_data = redis_cache.json().get("latest_plane_data")

        
    socketio.emit("latest_data", latest_plane_data)
    
# @socketio.on('init_connect')
# def handle_init(data):
#     print(f'received message: {str(data)}')
    
