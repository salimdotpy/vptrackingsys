from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..models import Passenger, Vehicle, db
from werkzeug.security import generate_password_hash
from ..utils import to_dict, uploadImage, getImageSize, imagePath
import re

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form.get("mobile")
        password = request.form.get("password")
        # Validation checks
        driver = Vehicle.query.filter_by(mobile=mobile).first()
        if driver is None or not driver.check_password(password):
            flash('Invalid Credential', ('error'))
            return redirect(request.referrer)
        elif not driver.status:
            flash('Contact Admin to activate your account', ('info'))
            return redirect(request.referrer)
        session['driver'] = to_dict(driver, Vehicle)
        flash('You\'ve successfully logged in!', ('success'))
        return redirect(url_for('driver.dashboard'))
    return render_template("login.html", pageTitle="Login Page")

@auth_bp.route("/register", methods=["GET", "POST"])
@auth_bp.route("/register/<who>", methods=["GET", "POST"])
def register(who="passenger"):
    if who not in ['passenger', 'vehicle']:
        return None, 404
    pageTitle = "Passenger Registration Page" if who == "passenger" else "Vehicle Registration Page"
    if request.method == "POST":
        if who == "passenger":
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
                if key !='email' and not val:
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
                    msg = ['You\'ve registered successfully, download your QR-Code!', 'success']
                except Exception as e:
                    db.session.rollback()
                    print(e); passenger = False
                    msg = ['Something went wrong, Please try again!', 'error']
            flash(msg[0], (msg[1]))
            return render_template("register.html", who=who, pageTitle=pageTitle, passenger=passenger)
    
        else:
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
                if (key !='email' and not val) or not image:
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
                    flash('You\'ve registered successfully,  login now please!', ('success'))
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    msg = ['Something went wrong, Please try again!', 'error']
            # print(request.form, request.files, sep='\n')
            flash(msg[0], (msg[1]))
    return render_template("register.html", who=who, pageTitle=pageTitle)

@auth_bp.route("/forget-password", methods=["GET", "POST"])
def forgetRestPass():
    msg = ''
    if request.method == 'POST' and 'forgotP' in request.form:
        # Create variables for easy access
        email = request.form['email']
        mobile = request.form['mobile']
        # Check if account exists
        user = Vehicle.query.filter_by(email=email, mobile=mobile).first()
        if user: return [mobile, True]
        else: return ['Invalid Credential!', False]
    if request.method == 'POST'and 'resetP' in request.form:
        # Create variables for easy access
        msg = ''
        npass = request.form['npass']
        cpass = request.form['cpass']
        mobile = request.form['mobile']
        # validation checks
        if not npass or not cpass or not mobile:
            msg = ['Please fill out the form!', 'error']
        elif npass != cpass:
            msg = ['Two password does not match!', 'error']
        else:
            update = Vehicle.query.filter_by(mobile=mobile).first()
            password = generate_password_hash(npass)
            update.password = password
            try:
                db.session.commit()
                return ['Password reset successfully!', 'success']
            except:
                db.session.rollback()
                return ['Unable to reset Password, Please try again!', 'error']
    return msg
