import sqlite3

def migrate():
    con = sqlite3.connect('app.db')
    cur = con.cursor()
    
    try:
        cur.execute("ATTACH DATABASE 'app_old.db' AS old_db")
        
        cur.execute("""
            INSERT OR IGNORE INTO plane (created_at, icao24, callsign, origin_country)
            SELECT MIN(created_at), icao24, callsign, origin_country 
            FROM old_db.plane_data 
            GROUP BY icao24;
        """)
        print(f"Migrated {cur.rowcount} unique planes.")
        
        cur.execute("""
            INSERT INTO plane_data (plane_icao24, time_fetched, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, sensors, geo_altitude, squawk, spi, position_source)
            SELECT icao24, time_fetched, time_position, last_contact, longitude, latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, sensors, geo_altitude, squawk, spi, position_source
            FROM old_db.plane_data;
        """)
        print(f"Migrated {cur.rowcount} plane data records.")
        
        con.commit()
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        con.close()

if __name__ == '__main__':
    migrate()
