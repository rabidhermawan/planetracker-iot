from src import socketio, redis_cache

from src.plane_data import opensky_fetch_plane_data
from config import MapBounds, SELECTED_MAP_BOUNDS


def opensky_broadcast_plane_data(area: str):
    print(f'Data fetched, broadcasting data')
    # Check redis cache first
    latest_plane_data = redis_cache.hgetall("latest_plane_data")
    
    if not latest_plane_data:
        print("Cache not found, fetch the data")
        _,_ = opensky_fetch_plane_data(area)
        latest_plane_data = redis_cache.hgetall("latest_plane_data")
        
    socketio.emit("latest_data", latest_plane_data)

@socketio.on('connect')
def handle_message():
    print(f'Connect : User connected, sending latest data')
    latest_plane_data = redis_cache.hgetall("latest_plane_data")
    
    if not latest_plane_data:
        print("Connect : Cache not found, fetch the data")
        _,_ = opensky_fetch_plane_data(SELECTED_MAP_BOUNDS)
        latest_plane_data = redis_cache.hgetall("latest_plane_data")
        
    socketio.emit("latest_data", latest_plane_data)
    
@socketio.on('init_connect')
def handle_init(data):
    print(f'received message: {str(data)}')
    
