from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "ff969ff4ecda8679c7e022ba88999d37"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


from app import oauth2
from app import routes