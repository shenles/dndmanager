from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache

app = Flask(__name__)
app.config.from_object(Config)
app.config["CACHE_TYPE"] = "simple"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
cache = Cache(app)

from app import routes, models
