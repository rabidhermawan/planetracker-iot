from flask import render_template
from src import app
from src.plane_data import opensky_fetch_plane_data

from config import MapBounds, SELECTED_MAP_BOUNDS

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
    opensky_fetch_plane_data(SELECTED_MAP_BOUNDS)
    return render_template('map.html', bounds=MapBounds[SELECTED_MAP_BOUNDS])