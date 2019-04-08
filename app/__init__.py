from flask import Flask
from cfg import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
### DATABASE ###
db = SQLAlchemy(app)
migrate = Migrate(app, db)

### LOGIN ###
login = LoginManager(app)
login.login_view = 'log_in'
from app import routes, models, errors
