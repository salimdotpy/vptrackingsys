from flask import Flask, flash, request, redirect
from .models import *
from .utils import parse_val
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

    @app.route("/api/updata-status/<table>/<id>/<key>/<val>")
    @app.route("/api/updata-status/<table>/<id>/<key>/<val>/<title>")
    def updataStatus(table, id, key, val, title='Status'):
        try:
            model = globals().get(table)
            snapshot = model.query.get(int(id))
            setattr(snapshot, key, parse_val(val))
            db.session.commit()
            msg = [f'{title} updated successfully!', 'success']
        except Exception as e:
            print(e)
            msg = [f'{str(e)}', 'error']
        flash(msg[0], (msg[1]))
        return redirect(request.referrer)

    return app