from flask import render_template, jsonify
from sqlalchemy import func, desc
from src import app, token, db
from src.opensky.helper import opensky_fetch_plane_data
from src.models import PlaneData, Plane
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

@app.route('/live_map')
def live_map():
    return render_template('map_loadbroadcast.html', bounds=Config.MapBounds[Config.SELECTED_MAP_BOUNDS])

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/analytics')
def analytics():
    # 1. Total unique planes in the most recent fetch
    latest_fetch_time = db.session.query(func.max(PlaneData.time_fetched)).scalar()
    
    if latest_fetch_time is None:
        return jsonify({
            "total_planes": 0,
            "avg_velocity": 0,
            "avg_altitude": 0,
            "top_countries": [],
            "on_ground": 0,
            "in_air": 0
        })

    # Query latest records
    latest_records_query = PlaneData.query.filter(PlaneData.time_fetched == latest_fetch_time)
    
    total_planes = latest_records_query.count()
    
    # 2. Avg velocity and altitude
    avg_stats = db.session.query(
        func.avg(PlaneData.velocity).label('avg_velocity'),
        func.avg(PlaneData.baro_altitude).label('avg_altitude')
    ).filter(PlaneData.time_fetched == latest_fetch_time).first()
    
    avg_velocity = round(avg_stats.avg_velocity, 2) if avg_stats.avg_velocity else 0
    avg_altitude = round(avg_stats.avg_altitude, 2) if avg_stats.avg_altitude else 0
    
    # 3. Top origin countries
    top_countries_query = db.session.query(
        Plane.origin_country, 
        func.count(PlaneData.id).label('count')
    ).select_from(PlaneData)\
     .join(Plane)\
     .filter(PlaneData.time_fetched == latest_fetch_time)\
     .group_by(Plane.origin_country)\
     .order_by(desc('count'))\
     .limit(5).all()
     
    top_countries = [{"country": str(c.origin_country), "count": c.count} for c in top_countries_query]
    
    # 4. On ground vs in air
    on_ground_count = latest_records_query.filter(PlaneData.on_ground == True).count()
    in_air_count = total_planes - on_ground_count

    return jsonify({
        "total_planes": total_planes,
        "avg_velocity": avg_velocity,
        "avg_altitude": avg_altitude,
        "top_countries": top_countries,
        "on_ground": on_ground_count,
        "in_air": in_air_count
    })