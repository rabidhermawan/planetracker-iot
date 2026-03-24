import os
# Refer to the executed file for base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
       
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'you-will-never-guess'

# la : lattitude, lo : longitude
MapBounds = {
        "SWISS": {
            "lamin": 40.8389,
            "lomin": 5.9962,
            "lamax": 47.8229,
            "lomax": 10.5226
        },
        "PERAK_PENANG": {
            "lamin": 3.620,
            "lomin": 100.11,
            "lamax": 5.989,
            "lomax": 101.87
        }
    }

        # [5.989, 101.87],  //Kanan Atas
        # [5.989, 100.11],
        # [3.620, 101.87],
        # [3.620, 100.11],

SELECTED_MAP_BOUNDS: str = "PERAK_PENANG"