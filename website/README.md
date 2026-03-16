# PLANETRACKER - IOT

WORK IN PROGRESS  
Web app that periodically fetches data from OpenSky API then display plane's location on an area and stores it on the database

## Current features
- Periodic plane data fetching from from OpenSky API
- Interactive map with real-time plane location analyzing

## Work In Progress
- Docker support
- View plane data detail and travel trail
- Detailed analytics

## How to run
0. Setup Redis for caching
```bash
docker run -p 6379:6379 my-valkey-bundle
```

1. Create a Python virtual environment, then enter the virtual environment
```shell
python -m venv .venv

# Linux
source .venv/Scripts/activate

# Windows
./.venv/Scripts/Activate.ps1
```

2. Download the dependencies
```shell
pip install -r requirements.txt
```

3. Create the .flaskenv file from the provided .flaskenv.example, modify the env files as needed
```shell
cp .flaskenv.example .flaskenv
```

3a. **ONLY RUN THIS WHEN MIGRATING NEW DATA**. Run the command below to migrate the database
```shell
flask db init
flask db migrate
```

3. Run the application. Currently it requires that you disable auto-reload/running more than one instance due to how APScheduler works.
```shell
flask run --no-reload

# For debugging
flask --debug --no-reload
```

## Software architecture
### WIP
