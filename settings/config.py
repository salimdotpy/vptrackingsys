import os
from dotenv import load_dotenv

# Determine which .env file to load
env = os.getenv("FLASK_ENV", "development")  # default to development
dotenv_path = f".env.{env}"

# Load environment variables from the selected file
load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "salimtech-vptrackingsys-app-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+mysqldb://root:@localhost/vptrackingsys")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

