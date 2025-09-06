from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from ..models import Passenger, Vehicle, db
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from ..utils import to_dict, uploadImage, getImageSize, imagePath
import re

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

@drive_bp.route("/logout")
def logout():
    session.pop('driver', None)
    flash('You have successfully logged out!', ('warning'))
    return redirect(url_for('auth.login'))

@drive_bp.route("/profile", methods=['POST'], endpoint="profile")
def profileUpdate():
    if 'driver' in session:
        driver = Vehicle.query.get(session['driver']['id'])
        # Create variables for easy access
        name = request.form.get("name").strip()
        email = request.form.get("email")
        mobile = request.form.get("mobile").strip()
        image = request.files.get("image")
        checkEmail = db.session.query(Vehicle).filter(Vehicle.email==email, Vehicle.id != driver.id).first()
        checkMobile = db.session.query(Vehicle).filter(Vehicle.mobile==mobile, Vehicle.id != driver.id).first()
        # Validation checks
        for key, val in request.form.items():
            if (key not in ['email', 'addDriver'] and not val):
                msg = ['Please fill out the form!', 'error']
        if checkEmail:
            msg = ["This email has been taken, please try another one", 'error']
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
            msg = ['Invalid email address!', 'error']
        elif not int(mobile) or len(mobile) != 11:
            msg = ['Invalid phone number!', 'error']
        elif checkMobile:
            msg = ['This phone number has been taken, please try another one', 'error']
        else:
            if image:
                image = uploadImage(image, imagePath('driver'), getImageSize(image), driver.image)
                driver.image = image if image else driver.image
            driver.name = name; driver.email = email; driver.mobile = mobile
            try:
                db.session.commit()
                msg = ['Profile updated successfully!', 'success']
            except:
                db.session.rollback()
                msg = ['Unable to update profile, please try again later!', 'error']
        session['driver'] = to_dict(driver, Vehicle)
        flash(msg[0], (msg[1]))
        return redirect(request.referrer)
    flash('Please login first!', ('warning'))
    return redirect(url_for('login'))

@drive_bp.route("/password", methods=['POST'], endpoint="password")
def passwordUpdate():
    if "driver" in session:
        driver = Vehicle.query.get(session['driver']['id'])
        # Create variables for easy access
        opass = request.form['opass']
        npass = request.form['npass']
        cpass = request.form['cpass']
        if not opass or not npass or not cpass:
            msg = ['Please fill out the form!', 'error']
        elif npass != cpass:
            msg = ['Two password does not match!', 'error']
        elif not driver.check_password(opass):
            msg = ['Old password does not match!', 'error']
        else:
            password = generate_password_hash(npass)
            driver.password = password
            try:
                db.session.commit()
                msg = ['Password updated successfully!', 'success']
            except:
                db.session.rollback()
                msg = ['Unable to update password, please try again later!', 'error']
            session['driver'] = to_dict(driver, Vehicle)
        flash(msg[0], (msg[1]))
        return redirect(request.referrer)
    flash('Please login first!', ('warning'))
    return redirect(url_for('login'))
