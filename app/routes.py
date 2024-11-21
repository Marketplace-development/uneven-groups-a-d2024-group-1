from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, Location, Reservation
from datetime import datetime
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
    message = None
    message_color = None  # Green for success, red for failure

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch the user by username
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            message = "Login Successful!"
            message_color = "green"
            return render_template('login.html', message=message, message_color=message_color)  # Show message before redirect
        else:
            message = "Login Failed."
            message_color = "red"
            return render_template('login.html', message=message, message_color=message_color)  # Show message if login failed

    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('main.signup'))

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=password_hash)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.success'))

    return render_template('signup.html')

@main.route('/success')
def success():
    return render_template('success.html')

@main.route('/main_page')
#@login_required
def main_page():
    return render_template('main_page.html')

@main.route('/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'POST':
        username = request.form.get("username")
        location_name = request.form.get("location_name")
        location_type = request.form.get("location_type")
        country = request.form.get("country")
        postal_code = request.form.get("postal_code")
        city = request.form.get("city")
        street = request.form.get("street")
        street_number = request.form.get("street_number")
        chairs = int(request.form.get("chairs"))

        def format_time(hour, minute):
            """Formats hour and minute into 'HH:mm'. Returns None for invalid/missing values."""
            if not hour or not minute:  # Check if either value is missing
                return None
            try:
                # Convert hour and minute to integers
                hour = int(hour)
                minute = int(minute)
                # Validate ranges (hour: 0-23, minute: 0-59)
                if 0 <= hour < 24 and 0 <= minute < 60:
                    return f"{hour:02}:{minute:02}"  # Return formatted time
            except ValueError:
                pass  # If conversion fails, return None
            return None

        
        # Use helper function to format times
        monday_open = format_time(request.form.get('monday_open'), request.form.get('monday_open_min'))
        monday_close = format_time(request.form.get('monday_close'), request.form.get('monday_close_min'))
        tuesday_open = format_time(request.form.get('tuesday_open'), request.form.get('tuesday_open_min'))
        tuesday_close = format_time(request.form.get('tuesday_close'), request.form.get('tuesday_close_min'))
        wednesday_open = format_time(request.form.get('wednesday_open'), request.form.get('wednesday_open_min'))
        wednesday_close = format_time(request.form.get('wednesday_close'), request.form.get('wednesday_close_min'))
        thursday_open = format_time(request.form.get('thursday_open'), request.form.get('thursday_open_min'))
        thursday_close = format_time(request.form.get('thursday_close'), request.form.get('thursday_close_min'))
        friday_open = format_time(request.form.get('friday_open'), request.form.get('friday_open_min'))
        friday_close = format_time(request.form.get('friday_close'), request.form.get('friday_close_min'))
        saturday_open = format_time(request.form.get('saturday_open'), request.form.get('saturday_open_min'))
        saturday_close = format_time(request.form.get('saturday_close'), request.form.get('saturday_close_min'))
        sunday_open = format_time(request.form.get('sunday_open'), request.form.get('sunday_open_min'))
        sunday_close = format_time(request.form.get('sunday_close'), request.form.get('sunday_close_min'))

        location_picture = request.form.get("location_picture")

        # Check if the user already has a location
        existing_location = Location.query.filter_by(username=username).first()
        if existing_location:
            flash("You can only upload one location. You already uploaded a location.", "danger")
            return redirect(url_for('main.locations'))

        new_location = Location(username=username, location_name=location_name, location_type=location_type,
                                country=country, postal_code=postal_code, city=city, street=street, street_number=street_number,
                                chairs=chairs, monday_open=monday_open, monday_close=monday_close, tuesday_open=tuesday_open, tuesday_close=tuesday_close,
                                wednesday_open=wednesday_open, wednesday_close=wednesday_close, thursday_open=thursday_open, thursday_close=thursday_close,
                                friday_open=friday_open, friday_close=friday_close, saturday_open=saturday_open, saturday_close=saturday_close,
                                sunday_open=sunday_open, sunday_close=sunday_close, location_picture=location_picture)

        db.session.add(new_location)
        db.session.commit()

        flash("Your location has been successfully added.", "success")
        return redirect(url_for('main.upload_location'))

    locations = Location.query.all()
    return render_template('locations.html')

@main.route('/reservations', methods=['GET', 'POST'])
@login_required
def reservations():
    # Debugging current_user
    print(f"Current User: {current_user}")
    print(f"Is authenticated: {current_user.is_authenticated}")

    if not current_user.is_authenticated:
        print("User is not authenticated!")
        return redirect(url_for('main.login'))  # Optional: Just in case
    
    locations = Location.query.all()

    if request.method == 'POST':
        location_id = request.form.get('location_id')
        username = request.form.get('username')
        reservation_time = request.form.get('reservation_time')
        number_of_guests = request.form.get('number_of_guests')
        study_time = request.form.get('study_time')

        # Get the location name from the selected location
        selected_location = Location.query.get(location_id)
        location_name = selected_location.location_name  # Retrieve the location name from the selected location

        # Parse the reservation_time as a datetime object
        reservation_datetime = datetime.strptime(reservation_time, "%Y-%m-%dT%H:%M")

        # Create a new reservation
        new_reservation = Reservation(
            user_id=current_user.id,  # Assuming `current_user` is available
            username = username,
            location_id=location_id,
            reservation_time=reservation_datetime,
            number_of_guests=int(number_of_guests),
            study_time=int(study_time),
            date=reservation_datetime.date(),  # Extract date from datetime
            time=reservation_datetime.time(),  # Extract time from datetime
        )

        # Save the new reservation to the database
        db.session.add(new_reservation)
        db.session.commit()

        # Flash a success message
        flash('Your reservation has been successfully created!', 'success')

        # Redirect to the 'reservation_successful' page after successful reservation
        return redirect(url_for('main.reservation_successful'))

    # Retrieve all the current reservations for the user
    user_reservations = Reservation.query.filter_by(user_id=current_user.id).all()

    # Render the reservation form with locations and current user reservations
    return render_template('reservations.html', locations=locations, reservations=user_reservations)

@main.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user.id:
        flash('You are not authorized to cancel this reservation.', 'error')
        return redirect(url_for('main.reservations'))

    db.session.delete(reservation)
    db.session.commit()
    flash('Reservation canceled.', 'success')
    return redirect(url_for('main.reservations'))


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))  # Redirect to login after logout

@main.route('/upload_location', methods=['GET','POST'])
def upload_location():
    # Logic for uploading location data goes here
    return render_template('upload_location.html')  # Redirect back to the locations page after the upload


@main.route('/reservation_successful', methods=['GET','POST'])
def reservation_successful():
    # Logic for uploading location data goes here
    return render_template('reservation_successful.html')  # Redirect back to the locations page after the upload

@main.route('/current_reservations', methods=['GET','POST'])
@login_required
def current_reservations():
    # Retrieve the current user's reservations
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    
    # Debugging: Print current user and reservations
    print(f"Current User: {current_user.username}")
    print(f"Reservations: {reservations}")

    return render_template('current_reservations.html', reservations=reservations)

@main.route('/location_bookings', methods=['GET','POST'])
@login_required
def location_bookings():
    # Fetch the location of the current logged-in user
    location = Location.query.filter_by(username=current_user.username).first()

    if not location:
        flash('You do not own any locations yet.', 'danger')
        return redirect(url_for('main.main_page'))

    # Get the reservations for this location
    reservations = Reservation.query.filter_by(location_id=location.id).all()

    # Render the template, passing the location and reservations
    return render_template('location_bookings.html', location=location, reservations=reservations)

