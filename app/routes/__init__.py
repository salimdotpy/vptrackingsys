from .main import main_bp
from .auth import auth_bp
from .driver import drive_bp
from .admin import admin_bp

blueprints = [main_bp, auth_bp, drive_bp, admin_bp]

def register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)

'''
import importlib
import pkgutil
from flask import Flask

def register_blueprints(app: Flask):
    """
    Automatically discover and register all blueprints
    inside the blueprints/ package.
    """
    package_name = __name__
    package = importlib.import_module(package_name)

    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if not is_pkg:  # skip folders
            module = importlib.import_module(f"{package_name}.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                # If attribute is a Blueprint, register it
                if getattr(attribute, "__class__", None).__name__ == "Blueprint":
                    app.register_blueprint(attribute)
'''
