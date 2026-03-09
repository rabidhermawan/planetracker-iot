from src import socketio

from src.plane_data import opensky_fetch_plane_data
from config import MapBounds, SELECTED_MAP_BOUNDS

@socketio.on('connect')
def handle_message(data):
    print(f'User connected, sending latest data')
    _, plane_data = opensky_fetch_plane_data(SELECTED_MAP_BOUNDS)
    socketio.emit('latest_data', plane_data)
    
@socketio.on('init_connect')
def handle_init(data):
    print(f'received message: {str(data)}')
    
    