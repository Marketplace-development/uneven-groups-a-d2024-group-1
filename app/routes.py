## This file creates a blueprint to register all routes

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, Location
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

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
            login_user(user) # Log in the user
            flash('Login Successful!', 'success')
            return redirect(url_for('main.main_page')) # Redirect to main page after signup
        else:
            # Invalid credentials
            flash('Invalid username or password, please try again.', 'error')
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
@login_required
def main_page():
    return render_template('main_page.html')

@main.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        # Extract form data
        location = Location(
            username=request.form.get("username"),
            phone_number=request.form.get("phone_number"),
            location_name=request.form.get("location_name"),
            location_type=request.form.get("location_type"),
            country=request.form.get("country"),
            postal_code=request.form.get("postal_code"),
            city=request.form.get("city"),
            street=request.form.get("street"),
            street_number=request.form.get("street_number"),
            bus=request.form.get("bus"),
            chairs=int(request.form.get("chairs")),
            monday_open=request.form.get("monday_open") + ":" + request.form.get("monday_open_min"),
            monday_close=request.form.get("monday_close") + ":" + request.form.get("monday_close_min"),
            tuesday_open=request.form.get("tuesday_open") + ":" + request.form.get("tuesday_open_min"),
            tuesday_close=request.form.get("tuesday_close") + ":" + request.form.get("tuesday_close_min"),
            wednesday_open=request.form.get("wednesday_open") + ":" + request.form.get("wednesday_open_min"),
            wednesday_close=request.form.get("wednesday_close") + ":" + request.form.get("wednesday_close_min"),
            thursday_open=request.form.get("thursday_open") + ":" + request.form.get("thursnesday_open_min"),
            thursday_close=request.form.get("thursday_close") + ":" + request.form.get("thursnesday_close_min"),
            friday_open=request.form.get("friday_open") + ":" + request.form.get("friday_open_min"),
            friday_close=request.form.get("friday_close") + ":" + request.form.get("friday_close_min"),
            saturday_open=request.form.get("saturday_open") + ":" + request.form.get("saturday_open_min"),
            saturday_close=request.form.get("saturday_close") + ":" + request.form.get("saturday_close_min"),
            sunday_open=request.form.get("sunday_open") + ":" + request.form.get("sunday_open_min"),
            sunday_close=request.form.get("sunday_close") + ":" + request.form.get("sunday_close_min"),
            location_picture=request.form.get("location_picture")
        )
        
        # Add to database
        db.session.add(location)
        db.session.commit()

        return redirect(url_for('success_page'))  # Redirect to a success page

    return render_template('locations.html')


@main.route('/reservations')
def reservations():
    return render_template('reservations.html')

@main.route('/upload_location', methods=['GET', 'POST'])
def upload_location():
    # Get form data
    username = request.form['username']
    phone_number = request.form['phone_number']
    location_name = request.form['location_name']
    location_type = request.form['location_type']
    other_location_type = request.form.get('other_location_type')
    address = request.form['address']
    chairs = request.form['chairs']
    monday_hours = request.form['monday_hours']
    tuesday_hours = request.form['tuesday_hours']
    # Continue for other days...
    location_picture = request.form['location_picture']

    # Validate form data and insert into the database
    if not phone_number or not location_name or not address:
        flash("Please fill out all required fields", "error")
        return redirect(url_for('main.locations'))

    # Add location to the database
    new_location = Location(
        username=username,
        phone_number=phone_number,
        location_name=location_name,
        location_type=location_type,
        other_location_type=other_location_type,
        address=address,
        chairs=chairs,
        monday_hours=monday_hours,
        tuesday_hours=tuesday_hours,
        location_picture=location_picture
    )

    db.session.add(new_location)
    db.session.commit()

    return redirect(url_for('main.upload_location'))