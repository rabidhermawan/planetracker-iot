# PLANETRACKER - IOT

WORK IN PROGRESS  
Web app that periodically fetches data from OpenSky API then display plane's location on an area and stores it on the database

## Current features
- Periodic plane data fetching from from OpenSky API
- Interactive map with real-time plane location analyzing
- Detailed analytics

## How to run
0. Setup Redis for caching and (optionally) Postgre Database
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

3. Create the .flaskenv file from the provided .flaskenv.example, modify the env files as needed
```shell
cp .flaskenv.example .flaskenv

# If using Postgre database
"postgresql://postgres:yourpassword@yourip:yourport/postgres
```

3a. **ONLY RUN THIS WHEN MIGRATING NEW DATA**. Run the command below to migrate the database
```shell
flask db migrate
flask db upgrade
```

3. Run the application. Currently it requires that you disable auto-reload/running more than one instance due to how APScheduler works.
```shell
flask run --no-reload

# For debugging
flask --debug --no-reload
```

## Software architecture
### WIP
