import os, random, string
from dotenv import load_dotenv
from urllib.parse import quote_plus



load_dotenv(override=True)  # load variables from .env
class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Set up the App SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))
    # Social AUTH context
    SOCIAL_AUTH_GOOGLE = False

    # Google Oauth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', None)
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', None)
    SESSION_TYPE = "filesystem"
    # Enable/Disable Google  Login
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        SOCIAL_AUTH_GOOGLE = True
    
    # Database configuration
    # Database configuration
    DB_NAME = os.getenv('DB_NAME'     , None)
    DB_USER = os.getenv('DB_USER'     , None)
    DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD'     , None))
    DB_HOST = os.getenv('DB_HOST'     , None)
    DB_PORT = os.getenv('DB_PORT'     , None)

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'poke__app/static/uploads')