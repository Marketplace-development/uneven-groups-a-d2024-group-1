from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, Location, Reservation
from datetime import datetime, timedelta
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_, func
from sqlalchemy.sql import text, func



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
        phonenumber = request.form.get('phonenumber')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic validation
        if not phonenumber.isdigit():
            flash('Phone number must contain only digits.', 'error')
            return redirect(url_for('main.signup'))
        
        if len(phonenumber) < 9 or len(phonenumber) > 15:
            flash('Phone number must be between 9 and 15 digits.', 'error')
            return redirect(url_for('main.signup'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('main.signup'))

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, phonenumber=phonenumber, password_hash=password_hash)

        try:
            # Add user to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.success'))
        except:
            # Handle duplicate entries (e.g., unique phone number or username constraint)
            db.session.rollback()
            flash('Username or phone number already exists.', 'error')
            return redirect(url_for('main.signup'))

    return render_template('signup.html')

@main.route('/success')
def success():
    return render_template('success.html')

@main.route('/main_page')
@login_required
def main_page():
    # Calculate the average student rating
    avg_rating = (
        db.session.query(func.avg(Reservation.student_rating))
        .filter(Reservation.user_id == current_user.id, Reservation.student_rating.isnot(None))
        .scalar()
    )
    avg_rating = round(avg_rating) if avg_rating else None  # Round to the nearest integer or set to None

    # Update the user's `user_rating` in the database
    user = User.query.get(current_user.id)
    user.user_rating = avg_rating
    db.session.commit()

    return render_template('main_page.html', avg_rating=avg_rating, user=current_user)

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

    if request.method == 'POST':
        # Get reservation details from the form
        username = request.form.get('username')
        reservation_time = request.form.get('reservation_time')
        number_of_guests = request.form.get('number_of_guests')
        study_time = request.form.get('study_time')

        # Validate and parse the reservation time
        try:
            reservation_datetime = datetime.strptime(reservation_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash('Invalid reservation time format. Please try again.', 'danger')
            return redirect(url_for('main.reservations'))

        # Filter locations based on availability
        available_locations = filter_available_locations(reservation_datetime, study_time, number_of_guests)

        # Pass the filtered locations to the location selection page
        return render_template(
            'select_location.html',
            location_data=available_locations,
            reservation_time=reservation_time,
            study_time=study_time,
            number_of_guests=number_of_guests,
        )

    # Render the reservation form
    return render_template('reservations.html')

@main.route('/select_location', methods=['GET', 'POST'])
@login_required
def select_location():
    # Initialiseer variabelen
    reservation_time = None
    study_time = None
    number_of_guests = None

    # Haal gegevens op van POST- of GET-verzoeken
    if request.method == 'POST':
        reservation_time = request.form.get('reservation_time')
        study_time = request.form.get('study_time')
        number_of_guests = request.form.get('number_of_guests')
    else:  # Voor GET-verzoeken
        reservation_time = request.args.get('reservation_time')
        study_time = request.args.get('study_time')
        number_of_guests = request.args.get('number_of_guests')

    # Controleer of de vereiste gegevens aanwezig zijn
    if not reservation_time or not study_time or not number_of_guests:
        flash("All fields are required to proceed.", "error")
        return redirect(url_for('main.reservations'))  # Stuur gebruiker terug naar het reserveringsformulier

    # Converteer en valideer de gegevens
    try:
        reservation_datetime = datetime.strptime(reservation_time, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Invalid reservation time format.", "error")
        return redirect(url_for('main.reservations'))

    try:
        study_time = int(study_time)
        number_of_guests = int(number_of_guests)
    except ValueError:
        flash("Study time and number of guests must be valid numbers.", "error")
        return redirect(url_for('main.reservations'))

    # Controleer of de reserveringsdatum in de toekomst ligt
    if reservation_datetime < datetime.now():
        flash("You can only make reservations for future dates and times.", "error")
        return redirect(url_for('main.reservations'))

    # Roep de functie aan om beschikbare locaties te filteren
    available_locations = filter_available_locations(reservation_datetime, study_time, number_of_guests)

    # Render de pagina met beschikbare locaties
    return render_template(
        'select_location.html',
        location_data=available_locations,
        reservation_time=reservation_time,
        study_time=study_time,
        number_of_guests=number_of_guests,
    )


@main.route('/confirm_reservation', methods=['POST'])
@login_required
def confirm_reservation():
    location_id = request.form.get('location_id')
    reservation_time = request.form.get('reservation_time')
    study_time = request.form.get('study_time')
    number_of_guests = int(request.form.get('number_of_guests'))

    if not location_id:
        flash('You must select a location to complete your reservation.', 'danger')
        return redirect(url_for('main.select_location'))

    reservation_datetime = datetime.strptime(reservation_time, "%Y-%m-%dT%H:%M")
    
    current_time = datetime.utcnow().replace(microsecond=0)

    print(f"Current time: {current_time}")
    print(f"Reservation time: {reservation_datetime}")

    if reservation_datetime < current_time:
        flash('You can only make reservations for the future.' , 'danger')
        return redirect(url_for('main.select_location'))

    reservation_end_time = reservation_datetime + timedelta(minutes=int(study_time))

    location = Location.query.get(location_id)
    if not location:
        flash('The selected location does not exist.', 'danger')
        return redirect(url_for('main.select_location'))
    
    # Calculate reserved seats for this location and time slot
    overlapping_reservations = Reservation.query.filter(
        Reservation.location_id == location.id,
        Reservation.reservation_time < reservation_end_time,
        (Reservation.reservation_time + timedelta(minutes=int(study_time))) > reservation_datetime,
    ).all()

    reserved_seats = sum(res.number_of_guests for res in overlapping_reservations)
    available_seats = location.chairs - reserved_seats

    if number_of_guests > available_seats:
        flash(f'Only {available_seats} seats are available at {location.location_name}.', 'danger')
        return redirect(url_for('main.select_location', reservation_time=reservation_time, study_time=study_time, number_of_guests=number_of_guests))

    # Create a new reservation
    new_reservation = Reservation(
        user_id=current_user.id,
        username=current_user.username,
        location_id=location_id,
        reservation_time=reservation_datetime,
        number_of_guests=number_of_guests,
        study_time=int(study_time),
        date=reservation_datetime.date(),
        time=reservation_datetime.time(),
    )

    db.session.add(new_reservation)
    db.session.commit()

    flash('Your reservation has been successfully created!', 'success')
    return redirect(url_for('main.reservation_successful'))


def filter_available_locations(reservation_datetime, study_time, number_of_guests):
    """
    Helper function to filter locations based on reservation time, study time, and number of guests.
    This includes handling locations that are open past midnight (e.g., from 10 PM to 2 AM).
    It dynamically calculates available seats based on existing reservations.
    """
    # Define the end time of the reservation based on the study time
    reservation_end_time = reservation_datetime + timedelta(minutes=int(study_time))

    # Query all locations
    all_locations = Location.query.all()
    available_locations = []

    for location in all_locations:
        # Calculate already reserved seats for this location and time slot
        existing_reservations = Reservation.query.filter(
            Reservation.location_id == location.id,
            Reservation.reservation_time < reservation_end_time, # Reservation starts before end time
            Reservation.reservation_time + timedelta(minutes=int(study_time)) > reservation_datetime # Reservation ends after the requested start time
        ).all()

        reserved_seats = sum(res.number_of_guests for res in existing_reservations)

        # Check if the location has enough seats left
        available_seats = location.chairs - reserved_seats
        if available_seats < int(number_of_guests):
            continue

        # Check if the location is open during the reservation period
        day_name = reservation_datetime.strftime('%A').lower()  # Get the day of the week in lowercase
        open_time_str = getattr(location, f"{day_name}_open")
        close_time_str = getattr(location, f"{day_name}_close")

        # If the location is closed on that day, skip it
        if not open_time_str or not close_time_str:
            continue

        try:
            # Convert strings to datetime.time objects
            open_time = datetime.strptime(open_time_str, "%H:%M").time()
            close_time = datetime.strptime(close_time_str, "%H:%M").time()
        except ValueError:
            # If the time format is invalid, skip this location
            continue

        # Convert opening and closing times to full datetime objects
        open_time_datetime = datetime.combine(reservation_datetime.date(), open_time)

        # Handle times that span past midnight
        if close_time < open_time:
            # Extend close_time to the next day
            close_time_datetime = datetime.combine(reservation_datetime.date() + timedelta(days=1), close_time)
        else:
            # Both open and close times are on the same day
            close_time_datetime = datetime.combine(reservation_datetime.date(), close_time)

        # Check if the reservation falls within the location's open hours
        if not (open_time_datetime <= reservation_datetime <= close_time_datetime):
            continue
        if not (open_time_datetime <= reservation_end_time <= close_time_datetime):
            continue

        # If all checks pass, add the location to the list of available locations
        available_locations.append({
            'location': location,
            'available_seats': available_seats  # Pass the dynamically calculated seats
        })
    return available_locations

@main.route('/cancel_reservation', methods=['POST'])
@login_required
def cancel_reservation():
    # Get the reservation ID from the submitted form data
    reservation_id = request.form.get('reservation_id')
    
    if not reservation_id:
        flash('No reservation specified for cancellation.', 'error')
        return redirect(url_for('main.reservations'))

    # Retrieve the reservation
    reservation = Reservation.query.get_or_404(reservation_id)

    # Check if the current user owns the reservation
    if reservation.user_id != current_user.id:
        flash('You are not authorized to cancel this reservation.', 'error')
        return redirect(url_for('main.reservations'))

    # Update the status to "canceled"
    reservation.status = "canceled"
    db.session.commit()

    flash('Reservation successfully canceled.', 'success')
    return redirect(url_for('main.current_reservations'))


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

@main.route('/current_reservations', methods=['GET', 'POST'])
@login_required
def current_reservations():
    if request.method == 'POST':
        # Process location rating submission
        reservation_id = request.form.get('reservation_id')
        location_rating = request.form.get('location_rating')

        if reservation_id and location_rating:
            reservation = Reservation.query.get_or_404(reservation_id)

            # Ensure the user owns the reservation
            if reservation.user_id == current_user.id:
                try:
                    location_rating = int(location_rating)
                    if 1 <= location_rating <= 5:
                        reservation.location_rating = location_rating
                        db.session.commit()
                        flash("Your rating has been saved successfully!", "success")
                    else:
                        flash("Invalid rating value. Please select a value between 1 and 5.", "error")
                except ValueError:
                    flash("Invalid rating input. Please try again.", "error")
            else:
                flash("You are not authorized to rate this reservation.", "error")
        else:
            flash("Missing reservation ID or rating value.", "error")

        return redirect(url_for('main.current_reservations'))

    reservations = Reservation.query \
        .join(Location, Reservation.location_id == Location.id) \
        .filter(Reservation.user_id == current_user.id).all()

    # Separate reservations by status
    active_reservations = [r for r in reservations if r.status == "active"]
    loc_del_reservations = [r for r in reservations if r.status == "loc_del"]
    expired_reservations = [r for r in reservations if r.status == "expired"]

    if loc_del_reservations:
        flash("Some of your reservations are no longer valid as their associated locations have been deleted.", "warning")

    # Call the function to expire old reservations
    expire_old_reservations(current_user.id)

    return render_template(
        'current_reservations.html', 
        reservations=active_reservations,
        expired_reservations=expired_reservations
    )

def expire_old_reservations(user_id):
    # Get current time
    now = datetime.now()

    # Query to find active reservations that should expire
    reservations_to_expire = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.status == "active",
        Reservation.reservation_time < now
    ).all()

    # Check each reservation to see if it should expire
    for reservation in reservations_to_expire:
        reservation.status = "expired"

    db.session.commit()

@main.route('/location_bookings', methods=['GET', 'POST'])
@login_required
def location_bookings():
    if request.method == 'POST':
        # Process location rating submission
        reservation_id = request.form.get('reservation_id')
        student_rating = request.form.get('student_rating')

        if reservation_id and student_rating:
            reservation = Reservation.query.get_or_404(reservation_id)

            # Ensure the user owns the location
            if reservation.location and reservation.location.user_id == current_user.id:
                try:
                    student_rating = int(student_rating)
                    if 1 <= student_rating <= 5:
                        reservation.student_rating = student_rating
                        db.session.commit()
                        flash("Your rating has been saved successfully!", "success")
                    else:
                        flash("Invalid rating value. Please select a value between 1 and 5.", "error")
                except ValueError:
                    flash("Invalid rating input. Please try again.", "error")
            else:
                flash("You are not authorized to rate this reservation.", "error")
        else:
            flash("Missing reservation ID or rating value.", "error")

        return redirect(url_for('main.location_bookings'))

    # Fetch the active location of the current logged-in user
    location = Location.query.filter_by(username=current_user.username, status='active').first()

    if not location:
        flash('You do not own any active locations.', 'danger')
        return redirect(url_for('main.main_page'))

    # Get active reservations for this location
    reservations = Reservation.query.filter_by(location_id=location.id, status='active').all()

    # Get expired reservations for this location
    expired_reservations = Reservation.query.filter_by(location_id=location.id, status='expired').all()

    # Calculate the average location rating
    avg_rating = (
        db.session.query(func.avg(Reservation.student_rating))
        .filter(Reservation.location_id == location.id, Reservation.student_rating.isnot(None))
        .scalar()
    )
    avg_rating = round(avg_rating) if avg_rating else None  # Round to nearest integer or None

    # Update the location's average rating in the database
    if avg_rating is not None:
        location.location_rating = avg_rating
        db.session.commit()

    # Render the template, passing the location and reservations
    return render_template(
        'location_bookings.html',
        location=location, 
        avg_rating=avg_rating,
        reservations=reservations,
        expired_reservations=expired_reservations
        )

@main.route('/delete_location', methods=['POST'])
@login_required
def delete_location():
    # Get the location ID from the form
    location_id = request.form.get('location_id')
    location = Location.query.filter_by(id=location_id, username=current_user.username, status="active").first()

    if not location:
        flash("Location not found or unauthorized action.", "danger")
        return redirect(url_for('main.location_bookings'))

    # Update the location's status to 'deleted'
    location.status = "deleted"

    # Update the status of all associated reservations to 'loc_del'
    reservations = Reservation.query.filter_by(location_id=location.id, status="active").all()
    for reservation in reservations:
        reservation.status = "loc_del"

    # Commit the changes to the database
    db.session.commit()

    flash(f"Location '{location.location_name}' has been deleted.", "success")
    return redirect(url_for('main.location_bookings'))