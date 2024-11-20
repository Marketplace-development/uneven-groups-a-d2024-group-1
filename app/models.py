from . import db
from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import TIMESTAMP

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    student_id = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # This column

    def __repr__(self):
        return f"<User {self.username}>"

# Location model to store location data
class Location(db.Model):
    __tablename__ = 'locations'  # Matches the table name in the database

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)  # Location owner's username
    phone_number = db.Column(db.String(15), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    location_type = db.Column(db.String(50), nullable=False)  # e.g., cafe, library
    country = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    street_number = db.Column(db.String(10), nullable=False)
    bus = db.Column(db.String(10), nullable=True)  # Optional
    chairs = db.Column(db.Integer, nullable=False)  # Number of available chairs
    # Opening hours for each day of the week
    monday_open = db.Column(db.String(5), nullable=True)
    monday_close = db.Column(db.String(5), nullable=True)
    tuesday_open = db.Column(db.String(5), nullable=True)
    tuesday_close = db.Column(db.String(5), nullable=True)
    wednesday_open = db.Column(db.String(5), nullable=True)
    wednesday_close = db.Column(db.String(5), nullable=True)
    thursday_open = db.Column(db.String(5), nullable=True)
    thursday_close = db.Column(db.String(5), nullable=True)
    friday_open = db.Column(db.String(5), nullable=True)
    friday_close = db.Column(db.String(5), nullable=True)
    saturday_open = db.Column(db.String(5), nullable=True)
    saturday_close = db.Column(db.String(5), nullable=True)
    sunday_open = db.Column(db.String(5), nullable=True)
    sunday_close = db.Column(db.String(5), nullable=True)
    location_picture = db.Column(db.String(200), nullable=True)  # Optional URL to the uploaded image
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Location {self.location_name} ({self.city})>"

# Reservation model to store reservations
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.relationship('Location', backref='reservations')
    user = db.relationship('User', backref='reservations')

    def __repr__(self):
        return f"<Reservation {self.date} at {self.time} for User {self.user_id}>"
