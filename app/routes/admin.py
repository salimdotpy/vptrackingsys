from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from ..models import Passenger, Vehicle, Admin, db
from sqlalchemy import or_
from ..utils import to_dict, uploadImage, imagePath, getImageSize
from werkzeug.security import generate_password_hash
import re

admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

@admin_bp.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    pageTitle = "Admin Dashboard"
    widget = {}
    if 'admin' in session:
        admin = Admin.query.get(session['admin']['id'])
        widget['new_driver'] = Vehicle.query.filter_by(status=False).count()
        widget['old_driver'] = Vehicle.query.filter_by(status=True).count()
        widget['passengers'] = Passenger.query.count()
        return render_template('admin/dashboard.html', pageTitle=pageTitle, admin=admin, widget=widget)
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login')+'#admin')

@admin_bp.route("/passengers", methods=['GET', 'POST'])
@admin_bp.route("/passengers/<status>", methods=['GET', 'POST'])
def passengers(status=None):
    pageTitle = "Manage Passenger"
    if 'admin' in session:
        admin = Admin.query.get(session['admin']['id'])
        passengers = Passenger.query.all()
        passengers = to_dict(passengers, Passenger)
        if status:
            pageTitle = "Manage Acitve Passengers" if status == "1" else "Manage Inacitve Passengers"
            passengers = Passenger.query.filter_by(status=status)
            passengers = to_dict(passengers, Passenger)
        
        if request.method == "POST" and 'addPassenger' in request.form:
            firstname = request.form.get("firstname").strip()
            lastname = request.form.get("lastname").strip()
            mobile = request.form.get("mobile").strip()
            email = request.form.get("email")
            address = request.form.get("address").strip()
            nokname = request.form.get("nokname").strip()
            nokmobile = request.form.get("nokmobile").strip()
            relationship = request.form.get("relationship")
            # Check if account exists using MySQL
            checkEmail = Passenger.query.filter_by(email=email).first()
            checkMobile = Passenger.query.filter_by(mobile=mobile).first()
            # Validation checks
            for key, val in request.form.items():
                if key not in ['email', 'addPassenger'] and not val:
                    msg = ['Please fill out the form!', 'error']
            firstname = firstname.split()
            if len(firstname) > 1:
                msg = ['First name must not contain space', 'error']
            if checkEmail:
                msg = ["This email has been taken, please try another one", 'error']
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
                msg = ['Invalid email address!', 'error']
            elif not int(mobile) or len(mobile) != 11:
                msg = ['Invalid phone number!', 'error']
            elif checkMobile:
                msg = ['This phone number has been taken, please try another one', 'error']
            else:
                try:
                    name = f"{firstname[0]} {lastname}"
                    nok_info = dict(nokname=nokname, nokmobile=nokmobile, relationship=relationship, address=address)
                    passenger = Passenger(name=name, email=email, mobile=mobile, nok_info=nok_info)
                    db.session.add(passenger)
                    db.session.commit()
                    passenger = passenger.query.get(passenger.id); passenger = to_dict(passenger, Passenger)
                    msg = ['New passenger added successfully!', 'success']
                except Exception as e:
                    db.session.rollback()
                    print(e); passenger = False
                    msg = ['Something went wrong, Please try again!', 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        if request.method == "POST" and 'updatePassenger' in request.form:
            id = request.form['id']
            firstname = request.form.get("firstname").strip()
            lastname = request.form.get("lastname").strip()
            mobile = request.form.get("mobile").strip()
            email = request.form.get("email")
            address = request.form.get("address").strip()
            nokname = request.form.get("nokname").strip()
            nokmobile = request.form.get("nokmobile").strip()
            relationship = request.form.get("relationship")
            # Check if account exists using MySQL
            uid = int(id)
            checkEmail = db.session.query(Passenger).filter(Passenger.email==email, Passenger.id != uid).first()
            checkMobile = db.session.query(Passenger).filter(Passenger.mobile==mobile, Passenger.id != uid).first()
            # Validation checks
            for key, val in request.form.items():
                if key not in ['email', 'updatePassenger'] and not val:
                    msg = ['Please fill out the form!', 'error']
            firstname = firstname.split()
            if len(firstname) > 1:
                msg = ['First name must not contain space', 'error']
            if checkEmail:
                msg = ["This email has been taken, please try another one", 'error']
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
                msg = ['Invalid email address!', 'error']
            elif not int(mobile) or len(mobile) != 11:
                msg = ['Invalid phone number!', 'error']
            elif checkMobile:
                msg = ['This phone number has been taken, please try another one', 'error']
            else:
                passenger = Passenger.query.get(int(uid))
                name = f"{firstname[0]} {lastname}"
                nok_info = dict(nokname=nokname, nokmobile=nokmobile, relationship=relationship, address=address)
                passenger.name = name; passenger.email = email; passenger.mobile = mobile; passenger.nok_info=nok_info
                try:
                    db.session.commit()
                    msg = ["Passenger's record Updated successfully!", 'success']
                except Exception as e:
                    db.session.rollback()
                    msg = ["Unable to update Passenger's record, please try again later!", 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        if request.method == 'POST' and 'deletePassenger' in request.form:
            # Create variables for easy access
            id = request.form['id']
            try:
                db.session.query(Passenger).filter(Passenger.id == id).delete()
                db.session.commit()
                msg =  ["Passenger's record deleted successfully!", 'success']
            except:
                db.session.rollback()
                msg =  ["Unable to delete Passenger's record, please try again later!", 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        return render_template('admin/manage-passenger.html', pageTitle=pageTitle, admin=admin, passengers=passengers)
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login')+'#admin')

@admin_bp.route("/drivers", methods=['GET', 'POST'])
@admin_bp.route("/drivers/<status>", methods=['GET', 'POST'])
def drivers(status=None):
    pageTitle = "Manage Driver"
    if 'admin' in session:
        admin = Admin.query.get(session['admin']['id'])
        drivers = Vehicle.query.all()
        drivers = to_dict(drivers, Vehicle)
        if status:
            pageTitle = "Manage Acitve Driver" if status == "1" else "Manage Unverified Driver"
            drivers = Vehicle.query.filter_by(status=status)
            drivers = to_dict(drivers, Vehicle)
        
        if request.method == "POST" and 'addDriver' in request.form:
            name = request.form.get("name").strip()
            email = request.form.get("email")
            mobile = request.form.get("mobile").strip()
            image = request.files.get("image")
            garages = request.form.getlist('garages[]')
            password = request.form['password']
            password2 = request.form['password2']
            vehicleNumber = request.form.get("vehicleNumber").strip()
            vehicleType = request.form.get("vehicleType")
            model = request.form.get("model")
            capacity = request.form.get("capacity")
            plateNumber = request.form.get("plateNumber")
            # Check if account exists using MySQL
            checkEmail = Vehicle.query.filter_by(email=email).first()
            checkMobile = Vehicle.query.filter_by(mobile=mobile).first()
            # Validation checks
            msg = False
            for key, val in request.form.items():
                if (key not in ['email', 'addDriver'] and not val) or not image:
                    msg = ['Please fill out the form!', 'error']
            if checkEmail:
                msg = ["This email has been taken, please try another one", 'error']
            if not garages or len(garages) < 2:
                msg = ["At least 2 garage name is required", 'error']
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
                msg = ['Invalid email address!', 'error']
            elif password != password2:
                msg = ["Two Password not matched", 'error']
            elif not int(mobile) or len(mobile) != 11:
                msg = ['Invalid phone number!', 'error']
            elif checkMobile:
                msg = ['This phone number has been taken, please try another one', 'error']
            elif not msg:
                try:
                    image = uploadImage(image, imagePath('driver'), getImageSize(image)) if image else None
                    vehicle_info = dict(vehicleNumber=vehicleNumber, vehicleType=vehicleType, model=model, capacity=capacity, plateNumber=plateNumber, garages=garages)
                    vehicle = Vehicle(name=name, email=email, mobile=mobile, image=image, vehicle_info=vehicle_info)
                    vehicle.set_password(password)
                    db.session.add(vehicle)
                    db.session.commit()
                    msg = ['New driver added successfully!', 'success']
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    msg = ['Something went wrong, Please try again!', 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        if request.method == "POST" and 'updateDriver' in request.form:
            id = request.form['id']
            name = request.form.get("name").strip()
            email = request.form.get("email")
            mobile = request.form.get("mobile").strip()
            image = request.files.get("image")
            garages = request.form.getlist('garages[]')
            vehicleNumber = request.form.get("vehicleNumber").strip()
            vehicleType = request.form.get("vehicleType")
            model = request.form.get("model")
            capacity = request.form.get("capacity")
            plateNumber = request.form.get("plateNumber")
            uid = int(id)
            checkEmail = db.session.query(Vehicle).filter(Vehicle.email==email, Vehicle.id != uid).first()
            checkMobile = db.session.query(Vehicle).filter(Vehicle.mobile==mobile, Vehicle.id != uid).first()
            # Validation checks
            for key, val in request.form.items():
                if (key not in ['email', 'addDriver'] and not val):
                    msg = ['Please fill out the form!', 'error']
            if checkEmail:
                msg = ["This email has been taken, please try another one", 'error']
            if not garages or len(garages) < 2:
                msg = ["At least 2 garage name is required", 'error']
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
                msg = ['Invalid email address!', 'error']
            elif not int(mobile) or len(mobile) != 11:
                msg = ['Invalid phone number!', 'error']
            elif checkMobile:
                msg = ['This phone number has been taken, please try another one', 'error']
            else:
                driver = Vehicle.query.get(int(uid))
                if image:
                    image = uploadImage(image, imagePath('driver'), getImageSize(image), driver.image)
                    driver.image = image if image else driver.image
                vehicle_info = dict(vehicleNumber=vehicleNumber, vehicleType=vehicleType, model=model, capacity=capacity, plateNumber=plateNumber, garages=garages)
                driver.name = name; driver.email = email; driver.mobile = mobile; driver.vehicle_info=vehicle_info
                try:
                    db.session.commit()
                    msg = ["Driver's record Updated successfully!", 'success']
                except Exception as e:
                    db.session.rollback()
                    msg = ["Unable to update Driver's record, please try again later!", 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        if request.method == 'POST' and 'deleteDriver' in request.form:
            # Create variables for easy access
            id = request.form['id']
            try:
                db.session.query(Vehicle).filter(Vehicle.id == id).delete()
                db.session.commit()
                msg =  ["Driver's record deleted successfully!", 'success']
            except:
                db.session.rollback()
                msg =  ["Unable to delete Driver's record, please try again later!", 'error']
            flash(msg[0], (msg[1]))
            return redirect(request.referrer)
        return render_template('admin/manage-driver.html', pageTitle=pageTitle, admin=admin, drivers=drivers)
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login')+'#admin')

@admin_bp.route("/profile", methods=['POST'], endpoint="profile")
def profileUpdate():
    if 'admin' in session:
        admin = Admin.query.get(session['admin']['id'])
        # Create variables for easy access
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        if not name or not mobile or not email:
            msg = ['Please fill out the form!', 'error']
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) or len(email) > 30:
            msg = ['Invalid email address!', 'error']
        elif not mobile or len(mobile) != 11:
            msg = ['Invalid phone number!', 'error']
        else:
            admin.name = name
            admin.email = email
            admin.mobile = mobile
            try:
                db.session.commit()
                msg = ['Profile updated successfully!', 'success']
            except:
                db.session.rollback()
                msg = ['Unable to update profile, please try again later!', 'error']
            session['admin'] = admin.to_dict()
        flash(msg[0], (msg[1]))
        return redirect(url_for('admin.dashboard'))
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login')+'#admin')

@admin_bp.route("/password", methods=['POST'], endpoint="password")
def passwordUpdate():
    if "admin" in session:
        admin = Admin.query.get(session['admin']['id'])
        # Create variables for easy access
        opass = request.form['opass']
        npass = request.form['npass']
        cpass = request.form['cpass']
        if not opass or not npass or not cpass:
            msg = ['Please fill out the form!', 'error']
        elif npass != cpass:
            msg = ['Two password must match!', 'error']
        elif not admin.check_password(opass):
            msg = ['Old password not match!', 'error']
        else:
            password = generate_password_hash(npass)
            admin.password = password
            try:
                db.session.commit()
                msg = ['Password updated successfully!', 'success']
            except:
                db.session.rollback()
                msg = ['Unable to update password, please try again later!', 'error']
            session['admin'] = admin.to_dict()
        flash(msg[0], (msg[1]))
        return redirect(url_for('admin.dashboard'))
    flash('Please login first!', ('warning'))
    return redirect(url_for('auth.login')+'#admin')

@admin_bp.route("/login", methods=['POST'])
def login():
    # Create variables for easy access
    username = request.form['username']
    password = request.form['password']
    # Validation checks
    admin = Admin.query.filter_by(name=username).first()
    if admin is None or not admin.check_password(password):
        flash('Invalid Credential', ('error'))
        return redirect(request.referrer+'#admin')
    session['admin'] = admin.to_dict()
    flash('You\'ve successfully logged in!', ('success'))
    return redirect(url_for('admin.dashboard'))

@admin_bp.route("/logout")
def logout():
    session.pop('admin', None)
    flash('You have successfully logged out!', ('warning'))
    return redirect(url_for('auth.login')+'#admin')
