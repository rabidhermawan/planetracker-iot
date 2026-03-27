from flask import render_template, jsonify, request
import sqlalchemy as sa #import func, desc
from src import app, token, db
from src.opensky.helper import opensky_fetch_plane_data
from src.models import PlaneData, Plane
from config import Config
from datetime import datetime, time, timedelta

from flask import redirect, url_for

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('dashboard'))

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

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/api/analytics')
def analytics():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Check if range is provided
    if start_date_str and end_date_str:
        try:
            start_datetime = datetime.combine(datetime.strptime(start_date_str, '%Y-%m-%d').date(), time.min)
            end_datetime = datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d').date(), time.max)
            
            base_query = PlaneData.query.filter(PlaneData.time_fetched >= start_datetime, PlaneData.time_fetched <= end_datetime)
            
            # Aggregate metrics over the period
            total_planes = base_query.with_entities(sa.func.count(sa.func.distinct(PlaneData.plane_id))).scalar() or 0
            
            avg_stats = db.session.query(
                sa.func.avg(PlaneData.velocity).label('avg_velocity'),
                sa.func.avg(PlaneData.baro_altitude).label('avg_altitude')
            ).filter(PlaneData.time_fetched >= start_datetime, PlaneData.time_fetched <= end_datetime).first()
            
            avg_velocity = round(avg_stats.avg_velocity, 2) if avg_stats and avg_stats.avg_velocity else 0
            avg_altitude = round(avg_stats.avg_altitude, 2) if avg_stats and avg_stats.avg_altitude else 0
            
            # Top countries
            top_countries_query = db.session.query(
                Plane.origin_country, 
                sa.func.count(sa.func.distinct(PlaneData.plane_id)).label('count')
            ).select_from(PlaneData)\
             .join(Plane)\
             .filter(PlaneData.time_fetched >= start_datetime, PlaneData.time_fetched <= end_datetime)\
             .group_by(Plane.origin_country)\
             .order_by(sa.desc('count'))\
             .limit(5).all()
            
            top_countries = [{"country": str(c.origin_country), "count": c.count} for c in top_countries_query]
            
            # Flight status approximation
            on_ground_count = base_query.filter(PlaneData.on_ground == True).count()
            in_air_count = base_query.filter(PlaneData.on_ground == False).count()
            
            return jsonify({
                "total_planes": total_planes,
                "avg_velocity": avg_velocity,
                "avg_altitude": avg_altitude,
                "top_countries": top_countries,
                "on_ground": on_ground_count,
                "in_air": in_air_count
            })
        except ValueError:
            pass # fallback if dates are invalid
            
    # Fallback: Live data snapshot
    date_str = request.args.get('date')
    query = db.session.query(sa.func.max(PlaneData.time_fetched))
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(target_date, time.min)
            end_datetime = datetime.combine(target_date, time.max)
            query = query.filter(PlaneData.time_fetched >= start_datetime, PlaneData.time_fetched <= end_datetime)
        except ValueError:
            pass 
            
    latest_fetch_time = query.scalar()
    
    if latest_fetch_time is None:
        return jsonify({
            "total_planes": 0,
            "avg_velocity": 0,
            "avg_altitude": 0,
            "top_countries": [],
            "on_ground": 0,
            "in_air": 0
        })

    latest_records_query = PlaneData.query.filter(PlaneData.time_fetched == latest_fetch_time)
    total_planes = latest_records_query.count()
    
    avg_stats = db.session.query(
        sa.func.avg(PlaneData.velocity).label('avg_velocity'),
        sa.func.avg(PlaneData.baro_altitude).label('avg_altitude')
    ).filter(PlaneData.time_fetched == latest_fetch_time).first()
    
    avg_velocity = round(avg_stats.avg_velocity, 2) if avg_stats.avg_velocity else 0
    avg_altitude = round(avg_stats.avg_altitude, 2) if avg_stats.avg_altitude else 0
    
    top_countries_query = db.session.query(
        Plane.origin_country, 
        sa.func.count(PlaneData.id).label('count')
    ).select_from(PlaneData)\
     .join(Plane)\
     .filter(PlaneData.time_fetched == latest_fetch_time)\
     .group_by(Plane.origin_country)\
     .order_by(sa.desc('count'))\
     .limit(5).all()
     
    top_countries = [{"country": str(c.origin_country), "count": c.count} for c in top_countries_query]
    
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
    
@app.route('/api/planes')
def api_planes():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    stmt = sa.select(Plane, PlaneData).join(PlaneData, Plane.id == PlaneData.plane_id)

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            
            stmt = stmt.where(
                sa.and_(
                    PlaneData.time_fetched >= start_date,
                    PlaneData.time_fetched < end_date
                )
            )
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    stmt = stmt.order_by(PlaneData.time_fetched.asc())

    # Execute the query
    results = db.session.execute(stmt).all()

    # Deduplicate in Python to ensure one row per plane for the frontend table
    planes_dict = {}
    for plane, data in results:
        planes_dict[plane.icao24] = {
            "icao24": plane.icao24,
            "callsign": plane.callsign,
            "origin": plane.origin_country,
        }

    planes_list = list(planes_dict.values())
    planes_list.sort(key=lambda x: (x['origin'] or 0), reverse=True)

    return jsonify(planes_list)

@app.route('/api/heatmap_data')
def api_heatmap_data():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Base query: select only non-null coordinates
    stmt = sa.select(PlaneData.latitude, PlaneData.longitude).where(
        sa.and_(
            PlaneData.latitude.is_not(None),
            PlaneData.longitude.is_not(None)
        )
    )

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            
            stmt = stmt.where(
                sa.and_(
                    PlaneData.time_fetched >= start_date,
                    PlaneData.time_fetched < end_date
                )
            )
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400
    else:
        # Fallback for "Live" mode (e.g., last 24 hours of flights)
        recent_threshold = datetime.utcnow() - timedelta(hours=24)
        stmt = stmt.where(PlaneData.time_fetched >= recent_threshold)

    results = db.session.execute(stmt).all()

    # Leaflet.heat expects a simple array of [lat, lng] arrays
    heat_points = [[row.latitude, row.longitude] for row in results]

    return jsonify(heat_points)