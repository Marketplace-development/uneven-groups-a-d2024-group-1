## This file is where tou would define the database models
## For now this is a placeholder example

from . import db
from datetime import datetime, timezone
from flask_login import UserMixin

# Define your models here
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    student_id = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    #created_at = db.Column(db.Datetime, default=lambda: datetime.now(timezone.utc))

class Location(db.Model):
    __tablename__ = 'Locations'  # Ensure this matches the table name in Supabase

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(15), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    location_type = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    street_number = db.Column(db.String(10), nullable=False)
    bus = db.Column(db.String(10))  # Optional, nullable
    chairs = db.Column(db.Integer, nullable=False)
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
    location_pictur = db.Column(db.String(100), nullable=False)  # URL to the uploaded image
    #created_at = db.Column(db.Datetime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Location {self.location_name} ({self.city})>"
    