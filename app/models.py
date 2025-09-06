from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Admin(db.Model, TimestampMixin):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    mobile = db.Column(db.String(40), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'mobile': self.mobile,
            'image': self.image,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at)
        }
    
class Passenger(db.Model, TimestampMixin):
    __tablename__ = "passengers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    image = db.Column(db.String(255), default=None, nullable=True)
    nok_info =  db.Column(db.JSON, nullable=True)
    qrcode = db.Column(db.String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.Boolean, default=True)

class Vehicle(db.Model, TimestampMixin):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=True)
    mobile = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    image = db.Column(db.String(255), default=None, nullable=True)
    vehicle_info =  db.Column(db.JSON, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<Vehicle {self.email}>"

class Setting(db.Model, TimestampMixin):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataKeys = db.Column(db.String(40), nullable=False)
    dataValues = db.Column(db.JSON, nullable=True)

class Trip(db.Model, TimestampMixin):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    From = db.Column(db.String(100), nullable=False)
    to = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    vehicle = db.relationship('Vehicle', foreign_keys=[vehicle_id], backref='trips')
    status = db.Column(db.String(40), nullable=True)

class PassengerTrip(db.Model, TimestampMixin):
    __tablename__ = "passenger_trips"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'), nullable=True)
    passenger = db.relationship('Passenger', foreign_keys=[passenger_id], backref='passengers')
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True)
    trip = db.relationship('Trip', foreign_keys=[trip_id], backref='passengers')
    latitude = db.Column(db.String(25), nullable=False)
    longitude = db.Column(db.String(25), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(40), nullable=True)

class TripLog(db.Model, TimestampMixin):
    __tablename__ = "trip_logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=True)
    trip = db.relationship('Trip', foreign_keys=[trip_id], backref='logs')
    passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'), nullable=True)
    passenger = db.relationship('Passenger', foreign_keys=[passenger_id], backref='logs')
    latitude = db.Column(db.String(25), nullable=False)
    longitude = db.Column(db.String(25), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(40), nullable=True)