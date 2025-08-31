from flask import Flask
from .models import *
from settings.config import DevelopmentConfig, ProductionConfig
import os
from flask_wtf.csrf import CSRFProtect

def create_app():
    
    app = Flask(
        __name__, 
        static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')),
        template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        )
    # Select config
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    csrf = CSRFProtect(app)
    db.init_app(app)

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app