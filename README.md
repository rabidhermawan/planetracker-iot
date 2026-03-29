# PLANETRACKER - IOT 
Web app that periodically fetches data from OpenSky API then display plane's location on an area and stores it on the database

## Current features
- Periodic plane data fetching from from OpenSky API
- Interactive map with real-time plane location analyzing
- Detailed analytics

## How to run
0. Setup Redis for caching and (optionally) Postgre Database.
```bash
docker run -p 6379:6379 -d --name valkey-0 valkey/valkey-bundle
docker run -p 5432:5432 -d --name postgres-0 -e POSTGRES_PASSWORD=yourpassword postgres
```

1. Create a Python virtual environment, then enter the virtual environment
```shell
python -m venv .venv

# Linux
source .venv/bin/activate

# Windows
./.venv/bin/Activate.ps1
```

2. Download the dependencies
```shell
pip install -r requirements.txt
```

3. Create the .flaskenv file from the provided .flaskenv.example, modify the env files as needed. If no database URL is provided, then SQLite will be used instead.
```shell
cp .flaskenv.example .flaskenv

# If using Postgre database
postgresql://postgres:yourpassword@yourip:yourport/postgres
```

3a. **ONLY RUN THIS WHEN MIGRATING NEW DATA**. Run the command below to migrate the database
```shell
flask db upgrade
```

4. Run the application. Currently it requires that you disable auto-reload/running more than one instance due to how APScheduler works.
```shell
flask run --no-reload

# For debugging
flask --debug --no-reload
```

## Software architecture
1. **OpenSky API** : provides the data required for plane analysis
2. **PostgreSQL / SQLite** : used for storing the data of the planes fetched from OpenSky
3. **Redis** : used for caching the latest plane data and airport data to reduce load when many users connect and provide seamless update to the Live Plane marker.
4. **Flask & SQLAlchemy** :  building the backend and provide HTML templating
5. **Bootstrap and Javascript** : Styling the website and also receive data from the Flask server and process incoming data before being displayed.

# Credit
Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic and Matthias Wilhelm.
"Bringing Up OpenSky: A Large-scale ADS-B Sensor Network for Research".
In Proceedings of the 13th IEEE/ACM International Symposium on Information Processing in Sensor Networks (IPSN), pages 83-94, April 2014.
