from . import db
from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import TIMESTAMP

# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    phonenumber = db.Column(db.String(15), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

# Location model to store location data
class Location(db.Model):
    __tablename__ = 'locations'  # Matches the table name in the database

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)  # Location owner's username
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    location_name = db.Column(db.String(100), nullable=False)
    location_type = db.Column(db.String(50), nullable=False)  # e.g., cafe, library
    country = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    street_number = db.Column(db.String(10), nullable=False)
    chairs = db.Column(db.Integer, nullable=False)

    # Opening hours for each day of the week
    monday_open = db.Column(db.String(10), nullable=True)
    monday_close = db.Column(db.String(10), nullable=True)
    tuesday_open = db.Column(db.String(10), nullable=True)
    tuesday_close = db.Column(db.String(10), nullable=True)
    wednesday_open = db.Column(db.String(10), nullable=True)
    wednesday_close = db.Column(db.String(10), nullable=True)
    thursday_open = db.Column(db.String(10), nullable=True)
    thursday_close = db.Column(db.String(10), nullable=True)
    friday_open = db.Column(db.String(10), nullable=True)
    friday_close = db.Column(db.String(10), nullable=True)
    saturday_open = db.Column(db.String(10), nullable=True)
    saturday_close = db.Column(db.String(10), nullable=True)
    sunday_open = db.Column(db.String(10), nullable=True)
    sunday_close = db.Column(db.String(10), nullable=True)

    status = db.Column(db.String(20), nullable=False, default='active')
    location_picture = db.Column(db.String(200), nullable=True)  # Optional URL to the uploaded image
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='locations')  # User who created the location

    def __repr__(self):
        return f"<Location {self.location_name} ({self.location_type})>"

# Reservation model to store reservations
class Reservation(db.Model):
    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)        # Student's username
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    study_time = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    location = db.relationship('Location', backref='reservations')
    user = db.relationship('User', backref='reservations')

    def __repr__(self):
        return f"<Reservation {self.id} by User {self.user_id} at Location {self.location_id} on {self.reservation_time} - Status: {self.status}>"
