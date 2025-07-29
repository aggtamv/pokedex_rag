from flask import Flask, app
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_dance.contrib.google import make_google_blueprint, google
from flask_session import Session
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_wtf import CSRFProtect
import os
from os import path
from datetime import timedelta
import logging
from dotenv import load_dotenv
from .extensions import db
from .models import User, OAuth
from .config import Config
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
csrf = CSRFProtect()

# Google OAuth blueprint (define at top-level)
google_bp = make_google_blueprint(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    scope=["openid", "email", "profile"],
    # **No storage argument here!**
)


def create_app():
    app = Flask(__name__)
    # Config
    app.config.from_object(Config)
    # Init extensions
    db.init_app(app)              
    Session(app)
    migrate = Migrate(app, db)
    csrf.init_app(app)
    app.permanent_session_lifetime = timedelta(minutes=90)
    # Load environment variables
    app.config['GOOGLE_CLIENT_ID'] = Config.GOOGLE_CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = Config.GOOGLE_CLIENT_SECRET
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    # Initialize the database
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SESSION_TYPE'] = 'filesystem'
    

    from .models import User
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    #Load our routes
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(google_bp, url_prefix="/login")
    # Print URL map to debug routes
    print(app.url_map)

    return app



def create_database(app):
    with app.app_context():
        db.create_all()
    print('Ensured all tables are created.')