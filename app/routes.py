## This file creates a blueprint to register all routes

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Blueprint for the main app
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch the user by username (ensure user exists)
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Password matches, proceed with login
            return redirect(url_for('main.main_page')) # Redirect to main page after signup
        else:
            # Invalid credentials
            return redirect(url_for('main.login')) # Redirect to the same login page to try again
        
    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        student_id = request.form.get('studentID')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if password and confirm_password match
        if password != confirm_password:
            # Flash an error message
            flash('Passwords do not match. Please try again.', 'error')
            # Redirect back to signup page
            return redirect(url_for('main.signup'))

        # Hash the password
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user instance
        new_user = User(username=username, email=email, student_id=student_id, password_hash=password_hash)

        # Add to the database session and commit
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.success'))  # Redirect to success page after signup
    
    return render_template('signup.html')

@main.route('/success')
def success():
    return render_template('success.html')

@main.route('/main_page')
def main_page():
    return render_template('main_page.html')

@main.route('/locations')
def locations():
    return render_template('locations.html')

@main.route('/reservations')
def reservations():
    return render_template('reservations.html')