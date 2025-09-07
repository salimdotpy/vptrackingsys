from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from ..models import Passenger, Vehicle, db
from sqlalchemy import or_
from ..utils import to_dict

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template('index.html')

@main_bp.route("/get-passenger/<id>")
def get_passenger(id):
    try:
        # Try integer lookup first
        if id.isdigit():
            passenger = Passenger.query.get(int(id))
            if passenger:
                return jsonify(to_dict(passenger, Passenger))

        # If not found by int, try QR code lookup
        passenger = Passenger.query.filter_by(qrcode=id).first()
        if passenger:
            return jsonify(to_dict(passenger, Passenger))

        # Nothing found
        return jsonify({'err': "Passenger not found!"}), 500

    except Exception as e:
        return jsonify({'err': str(e)}), 500


@main_bp.route("/qrcode", methods=["GET", "POST"])
def qrcode():
    passenger = False
    if request.method == "POST":
        mobile = request.form.get("mobile")
        # Placeholder logic
        if not mobile.strip():
            msg = ['Your phone number or email address is required to retrieve qrcode', 'error']
        else:
            passenger = db.session.query(Passenger).filter(or_(Passenger.mobile==mobile, Passenger.email==mobile)).first()
            if not passenger:
                flash("Record not found", ("error"))
                return redirect(url_for('main.index'))
            passenger = to_dict(passenger, Passenger)
            msg = ['Your qrcode retrieved successfully!', 'success']
        flash(msg[0], (msg[1]))
    return render_template('retriveqrcode.html', pageTitle="Retrieve QR-Code", passenger=passenger)
