from os import getenv
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from redis import Redis
redis_cache = Redis(host=getenv("REDIS_HOST") or "localhost", port=6379, decode_responses=True)

socketio = SocketIO(app)
from src import socket
socketio.run(app)

scheduler = BackgroundScheduler()
from src import background_tasks
scheduler.start()

from src import routes, models