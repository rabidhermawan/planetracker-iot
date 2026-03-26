import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path, override=True)

class Config(object):
    DEBUG = False
    TESTING = False
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
       
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'you-will-never-guess'
    
    # REDIS
    REDIS_URL = os.environ.get("REDIS_URL")
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT= int(os.environ.get("REDIS_PORT") or 6379)
    
    # API Settings
    API_FETCH_INTERVAL = int(os.environ.get("API_FETCH_INTERVAL") or 60)
    
    # OPENSKY Module
    OPENSKY_API_URL = os.environ.get("OPENSKY_API_URL") or "https://opensky-network.org/api"
    OPENSKY_TOKEN_URL = os.environ.get("OPENSKY_TOKEN_URL") or "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    OPENSKY_CLIENT_ID = os.environ.get("OPENSKY_CLIENT_ID") or "your_client_id"
    OPENSKY_CLIENT_SECRET = os.environ.get("OPENSKY_CLIENT_SECRET") or "your_client_secret"
    
    # How many seconds before expiry to proactively refresh the token.
    OPENSKY_TOKEN_REFRESH_MARGIN = int(os.environ.get("OPENSKY_TOKEN_REFRESH_MARGIN") or 30)
    
    SELECTED_MAP_BOUNDS = os.environ.get("SELECTED_MAP_BOUNDS") or "SWISS"
    
    MapBounds = {
        "SWISS": {
            "lamin": 45.8389,
            "lomin": 5.9962,
            "lamax": 47.8229,
            "lomax": 10.5226
        },
        "PERAK_PENANG": {
            "lamin": 3.620,
            "lomin": 100.11,
            "lamax": 5.989,
            "lomax": 101.87
        },
        "LONDON": {
            "lamin": 51.0,
            "lomin": -1.0,
            "lamax": 52.5,
            "lomax": 1.5
        }
    }
    
# la : lattitude, lo : longitude


        # [5.989, 101.87],  //Kanan Atas
        # [5.989, 100.11],
        # [3.620, 101.87],
        # [3.620, 100.11],

