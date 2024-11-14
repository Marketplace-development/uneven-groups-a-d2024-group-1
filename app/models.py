## This file is where tou would define the database models
## For now this is a placeholder example

from . import db
from datetime import datetime, timezone

# Define your models here
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    student_id = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    #created_at = db.Column(db.Datetime, default=lambda: datetime.now(timezone.utc))