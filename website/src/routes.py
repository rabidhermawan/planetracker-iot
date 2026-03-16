from flask import render_template
from src import app, token
from src.opensky.helper import opensky_fetch_plane_data
from config import Config

@app.route('/')
@app.route('/index')
def index():
    user = {'username':'test'}
    return render_template('index.html', title='Index', user=user)

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/test_fetch')
def test_fetch_latest():
    _, plane_data = opensky_fetch_plane_data(Config.SELECTED_MAP_BOUNDS, token)
    return render_template('map_loadjson.html', bounds=Config.MapBounds[Config.SELECTED_MAP_BOUNDS], plane_data=plane_data)

@app.route('/test_broadcast')
def test_broadcast():
    return render_template('map_loadbroadcast.html', bounds=Config.MapBounds[Config.SELECTED_MAP_BOUNDS])