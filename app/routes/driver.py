from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from ..models import Trip, TripLog, PassengerTrip, Passenger, Vehicle, db
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from ..utils import to_dict, uploadImage, getImageSize, imagePath, parse_record
import re

drive_bp = Blueprint("driver", __name__, url_prefix='/driver')

@drive_bp.route("/dashboard")
def dashboard():
    pageTitle = "Driver Dashboard"
    widget = {}
    if 'driver' in session:
        driver = Vehicle.query.get(session['driver']['id'])
        widget['danger_trip'] = Trip.query.filter_by(vehicle_id=driver.id, status='danger').count()
        widget['pending_trip'] = Trip.query.filter_by(vehicle_id=driver.id, status='pending').count()
        widget['success_trip'] = Trip.query.filter_by(vehicle_id=driver.id, status='success').count()
        widget['logs'] = TripLog.query.filter(TripLog.trip.has(vehicle_id=driver.id)).count()
        return render_template('dashboard.html', pageTitle=pageTitle, driver=driver, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login'))

@drive_bp.route("/trips", methods=['GET', 'POST'])
@drive_bp.route("/trips/<status>", methods=['GET', 'POST'])
def trips(status=None):
    if 'driver' in session:
        driver = Vehicle.query.get(session['driver']['id'])
        records = Trip.query.filter_by(vehicle_id=driver.id).all()
        trips = parse_record(records, Trip, passengers=PassengerTrip)
        pageTitle = f"Manage Trips"
        if status:
            pageTitle = f"Manage {status.capitalize()} Trips"
            records = Trip.query.filter_by(vehicle_id=driver.id, status=status).all()
            trips = parse_record(records, Trip, passengers=PassengerTrip)
        
        if request.method == "POST" and 'addTrip' in request.form:
            # Create variables for easy access
            From = request.form.get("From")
            to = request.form.get("to")
            description = request.form.get("description").strip()
            # Validation checks
            checkTrip  = Trip.query.filter_by(vehicle_id=driver.id, status='pending').first()
            for key, val in request.form.items():
                if (key not in ['description', 'addTrip'] and not val):
                    msg = ['Please fill out the form!', 'error']
            if From == to:
                msg = ["Starting Point and Destination can't be the same", 'error']
            elif checkTrip:
                msg = ["Can't have more than one uncompleted trip!", 'error']
            else:
                trip = Trip(From=From, to=to, description=description, vehicle_id=driver.id, status='pending')
                db.session.add(trip)
                try:
                    db.session.commit()
                    msg = ['Trip created successfully!', 'success']
                except:
                    db.session.rollback()
                    msg = ['Unable to create trip, please try again later!', 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        return render_template('manage-trip.html', pageTitle=pageTitle, driver=driver, trips=trips)
    flash('Please login first!', ('warning'))
    return redirect(url_for('login'))

@drive_bp.route("/passengers/<id>", methods=['GET', 'POST'])
@drive_bp.route("/passengers/<id>/<status>", methods=['GET', 'POST'])
def passengers(id, status=None):
    if not id:
        return redirect(request.referrer)
    if 'driver' in session:
        driver = Vehicle.query.get(session['driver']['id'])
        trip = Trip.query.get(id)
        records = PassengerTrip.query.filter_by(trip_id=id).all()
        passengers = parse_record(records, PassengerTrip, passenger=Passenger)
        pageTitle = f"Manage {trip.From} to {trip.to} Passengers"
        if status:
            status = ''.join(status.split('-'))
            pageTitle = f"Manage {status.capitalize()} {trip.From} to {trip.to} Passengers"
            records = PassengerTrip.query.filter_by(trip_id=id, status=status).all()
            passengers = parse_record(records, PassengerTrip, passenger=Passenger)
        
        if request.method == "POST" and 'add_passenger' in request.form:
            # Create variables for easy access
            passenger_id = request.form.get("id")
            latitude = request.form.get("lat")
            longitude = request.form.get("lng")
            # Validation checks
            checkTrip  = PassengerTrip.query.filter_by(passenger_id=passenger_id, trip_id=id).first()
            for key, val in request.form.items():
                if (key not in ['add_passenger'] and not val):
                    msg = ['Unable to retrieve users location!', 'error']
            if checkTrip:
                msg = ["This passenger already signed in to this trip!", 'warning']
            else:
                passenger = PassengerTrip(passenger_id=passenger_id, trip_id=id, latitude=latitude, longitude=longitude, status='signin')
                db.session.add(passenger)
                try:
                    db.session.commit()
                    msg = ['Passenger signed in successfully!', 'success']
                except:
                    db.session.rollback()
                    msg = ['Unable to sign passenger in, please try again later!', 'error']
            return jsonify({"msg": msg[0], "icon": msg[1]})
        
        if request.method == "POST" and 'remove_passenger' in request.form:
            # Create variables for easy access
            passenger_id = request.form.get("id")
            # Validation checks
            checkTrip  = PassengerTrip.query.filter_by(passenger_id=passenger_id, trip_id=id).first()
            if not checkTrip:
                msg = ["This passenger not found in this trip", 'error']
            elif checkTrip.status == "signout":
                msg = ["This passenger already signed out!", 'warning']
            else:
                checkTrip.status = "signout"
                try:
                    db.session.commit()
                    msg = ['Passenger signed out successfully!', 'success']
                except:
                    db.session.rollback()
                    msg = ['Unable to sign passenger out, please try again later!', 'error']
            return jsonify({"msg": msg[0], "icon": msg[1]})
        return render_template('manage-passenger.html', pageTitle=pageTitle, driver=driver, passengers=passengers, trip=trip)
    flash('Please login first!', ('warning'))
    return redirect(url_for('login'))

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

@drive_bp.route("/logout")
def logout():
    session.pop('driver', None)
    flash('You have successfully logged out!', ('warning'))
    return redirect(url_for('auth.login'))
