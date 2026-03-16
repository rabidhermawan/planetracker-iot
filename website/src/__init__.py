from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

from src.opensky.token_manager import OpenSkyTokenManager

app = Flask(__name__)
app.config.from_object(Config)


# Establish cache and Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from redis import Redis
redis_cache = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# Establish plane fetching logic
token = OpenSkyTokenManager()

# Establish socket
socketio = SocketIO(app)
from src import socket
socketio.run(app)

# Establish background scheduler
scheduler = BackgroundScheduler()
from src import background_tasks
scheduler.start()

from src import routes, models