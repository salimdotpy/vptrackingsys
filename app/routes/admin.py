from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from ..models import Passenger, Vehicle, Admin, db
from sqlalchemy import or_
from ..utils import to_dict
from werkzeug.security import generate_password_hash
import re

admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

@admin_bp.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    pageTitle = "Admin Dashboard"
    widget = {}
    if 'admin' in session:
        admin = Admin.query.get(session['admin']['id'])
        widget['new_driver'] = db.session.query(Vehicle).filter_by(status=False).count()
        widget['passengers'] = Passenger.query.count()

        # school = School.query.all()
        # widget['school'] = [sch.to_dict(True) for sch in school if sch.parent_id == None]
        # widget['representative'] = Representative.query.all()
        # widget['campuses'] = [camp.to_dict(True) for camp in school if camp.parent_id or not camp.campuses]
        # widget['buildings'] = Building.query.all()
        return render_template('admin/dashboard.html', pageTitle=pageTitle, admin=admin, widget=widget)
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
