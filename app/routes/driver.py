from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from ..models import Passenger, Vehicle, db
from sqlalchemy import or_
from ..utils import to_dict

drive_bp = Blueprint("driver", __name__, url_prefix='/driver')

@drive_bp.route("/dashboard")
def dashboard():
    pageTitle = "Driver Dashboard"
    widget = {}
    if 'driver' in session:
        driver = Vehicle.query.get(session['driver']['id'])
        return render_template('dashboard.html', pageTitle=pageTitle, driver=driver, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login'))
