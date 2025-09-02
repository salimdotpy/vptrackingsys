import os
from dotenv import load_dotenv

# Determine which .env file to load
env = os.getenv("FLASK_ENV", "development")  # default to development

# Load environment variables from the selected file
try:
    dotenv_path = os.path.expanduser('~/mysite')
    load_dotenv(os.path.join(dotenv_path, '.env.production'))
except:
    load_dotenv('.env.development')


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "salimtech-vptrackingsys-app-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+mysqldb://root:@localhost/vptrackingsys")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

