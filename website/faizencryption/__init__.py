from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pathlib import Path
import os

# App constructor
app = Flask (__name__)
app.permantent_session_lifetime = timedelta(minutes=5)

# Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "data", "users.sqlite")

upload_path = os.path.join(BASE_DIR, "upload")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config['SECRET_KEY'] = "23636bd97c12f839505bfcdd11d7712bba605035c1c84c2524aad37c2f62c462c479277acc1e2b3084597c260c7a959e"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = upload_path

# Logging purposes
app.config['CRYPTO_LOG_PATH'] = os.path.join(BASE_DIR, 'log', 'enc_dec_log.jsonl')
Path(os.path.dirname(app.config['CRYPTO_LOG_PATH'])).mkdir(parents=True, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from faizencryption import routes
