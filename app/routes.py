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

from flask import redirect, url_for

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
            return redirect(url_for('main.main_page'))  # Redirect to the main page after login
        else:
            message = "Login Failed."
            message_color = "red"
            return render_template('login.html', message=message, message_color=message_color)  # Show message if login failed

    return render_template('login.html', message=message, message_color=message_color)


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
            return redirect(url_for('main.login'))
        except:
            # Handle duplicate entries (e.g., unique phone number or username constraint)
            db.session.rollback()
            flash('Username or phone number already exists.', 'error')
            return redirect(url_for('main.signup'))

    return render_template('signup.html')

@main.route('/main-page', methods=['GET', 'POST'])
@login_required
def main_page():
    # Highlighted locations
    highlighted_locations = get_highlighted_locations()
    return render_template('main-page.html', user=current_user, highlighted_locations=highlighted_locations)

def get_highlighted_locations():
    # Calculate the start and end of the previous week
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday() + 7)  # Start of last week (Monday)
    end_of_week = start_of_week + timedelta(days=7)  # End of last week (Sunday)

    # Query to find the top 3 location with the highest average rating in the previous week
    highest_rated_locations = db.session.query(
        Reservation.location_id,
        func.avg(Reservation.location_rating).label('average_rating')
    ).filter(
        Reservation.reservation_time.between(start_of_week, end_of_week)  # Filter by reservation time during last week
    ).group_by(Reservation.location_id).order_by(func.avg(Reservation.location_rating).desc()).limit(3).all()

    # Get the details of the locations with the highest average ratings
    locations = [Location.query.get(location.location_id) for location in highest_rated_locations]
    return locations


@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # Get previous reservations made by the current user
    reservations = Reservation.query.filter(
        Reservation.user_id == current_user.id,
        Reservation.status == "expired"
    ).order_by(Reservation.date.desc()).all()


    # Get the location of the logged-in user
    location = Location.query.filter_by(user_id=current_user.id, status="active").first()

    # Query all bookings for this location (only expired ones, if the location exists)
    if location:
        bookings = Reservation.query.filter(
            Reservation.location_id == location.id,
            Reservation.status == "expired"
        ).order_by(Reservation.date.desc()).all()
    else:
        bookings = []  # No location or no active location found for the logged-in user

    # Fetch the active location of the current logged-in user
    location = Location.query.filter_by(user_id=current_user.id, status='active').first()

    # Get the current date
    today = datetime.today()

    # Get the start of the week (Monday) and the end of the week (Sunday)
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Calculate the number of completed sessions this week
    completed_sessions = db.session.query(Reservation).filter(
        Reservation.user_id == current_user.id,  # Filter by current user
        Reservation.date >= start_of_week.date(),  # Reservations this week
        Reservation.date <= end_of_week.date(),  # Reservations this week
        Reservation.status == 'expired',  # Only active (completed) reservations
        Reservation.date < today.date()  # Only count past reservations (before today)
    ).count()

    # Calculate the total study time for completed sessions this week
    completed_study_time = db.session.query(db.func.sum(Reservation.study_time)).filter(
        Reservation.user_id == current_user.id,  # Filter by current user
        Reservation.date >= start_of_week.date(),  # Reservations this week
        Reservation.date <= end_of_week.date(),  # Reservations this week
        Reservation.status == 'expired',  # Only active (completed) reservations
        Reservation.date < today.date()  # Only count past reservations (before today)
    ).scalar() or 0  # Use 0 if no study time exists

    # Get the target study time and sessions for the week from the user model
    target_study_time = current_user.minutes_target if current_user.minutes_target else 0  # Fallback to 0
    target_sessions = current_user.sessions_target if current_user.sessions_target else 0  # Fallback to 0

    # Check if the user has reached their targets
    study_time_reached = completed_study_time >= target_study_time if target_study_time else False
    sessions_reached = completed_sessions >= target_sessions if target_sessions else False

    # Prepare the congratulations message
    congratulations_message = ""
    if study_time_reached and sessions_reached:
        congratulations_message = "Congratulations, you reached both your study time and session targets this week!"
    elif study_time_reached:
        congratulations_message = "Congratulations, you reached your study time target this week!"
    elif sessions_reached:
        congratulations_message = "Congratulations, you reached your study session target this week!"

    # Format the study times in hours and minutes
    completed_hours, completed_minutes = divmod(completed_study_time, 60)
    target_hours, target_minutes = divmod(target_study_time, 60)

    # Format the dates to display "2 December - 8 December"
    start_of_week_str = start_of_week.strftime('%d %B')  # Day Month (e.g., 2 December)
    end_of_week_str = end_of_week.strftime('%d %B')  # Day Month (e.g., 8 December)

    # Combine the start and end of the week into one string
    week_range = f"{start_of_week_str} - {end_of_week_str}"
    if request.method == 'POST':
        try:
            # Handle setting the study time target (minutes)
            if 'hours' in request.form and 'minutes' in request.form:
                hours = request.form['hours']
                minutes = request.form['minutes']
                total_minutes = int(hours) * 60 + int(minutes)
                current_user.minutes_target = total_minutes

            # Handle setting the study sessions target
            if 'sessions_target' in request.form:
                sessions_target = request.form['sessions_target']
                current_user.sessions_target = int(sessions_target)

            # Handle deleting the study time target (minutes)
            if 'delete_minutes_target' in request.form:
                delete_target(current_user, 'minutes')

            # Handle deleting the study sessions target
            if 'delete_sessions_target' in request.form:
                delete_target(current_user, 'sessions')

            # Commit all changes in one transaction
            db.session.commit()
            flash("Targets updated successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the target: {str(e)}", "error")

        return redirect(url_for('main.account'))

    return render_template('account.html', user=current_user, week_range=week_range,
                           completed_sessions=completed_sessions, target_sessions=target_sessions,
                           completed_study_time=completed_study_time, target_study_time=target_study_time,
                           completed_hours=completed_hours, completed_minutes=completed_minutes,
                           target_hours=target_hours, target_minutes=target_minutes,
                           congratulations_message=congratulations_message, 
                           reservations=reservations, location=location, bookings=bookings)

@main.route('/update_user_info', methods=['POST'])
@login_required
def update_user_info():
    try:
        # Get the form data
        username = request.form.get('username')
        phonenumber = request.form.get('phonenumber')

        # Update user information
        if username:
            current_user.username = username
        if phonenumber:
            current_user.phonenumber = phonenumber

        db.session.commit()
        flash("Your information was updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "error")

    # Redirect back to the account page
    return redirect(url_for('main.account'))

def delete_target(user, target_type):
    """ Deletes the specified target for a user. """
    try:
        if target_type == 'minutes':
            user.minutes_target = None
        elif target_type == 'sessions':
            user.sessions_target = None
        else:
            return "Invalid target type specified."

        # Commit the changes to the database
        db.session.commit()
        return "Target deleted successfully."
    except Exception as e:
        db.session.rollback()
        return f"An error occurred while deleting the target: {str(e)}"

@main.route('/delete_location', methods=['POST'])
@login_required
def delete_location():
    # Get the location ID from the form
    location_id = request.form.get('location_id')
    location = Location.query.filter_by(id=location_id, user_id=current_user.id, status="active").first()

    if not location:
        flash("Location not found or unauthorized action.", "danger")
        return redirect(url_for('main.account'))

    # Update the location's status to 'deleted'
    location.status = "deleted"

    # Update the status of all associated reservations to 'loc_del'
    reservations = Reservation.query.filter_by(location_id=location.id, status="active").all()
    for reservation in reservations:
        reservation.status = "loc_del"

    # Commit the changes to the database
    db.session.commit()

    flash(f"Location '{location.location_name}' has been deleted.", "success")
    return redirect(url_for('main.account'))
    
@main.route('/all-locations', methods=['GET'])
@login_required
def all_locations():
    # Get all active filters from the URL
    sort_order = request.args.get('sort', '')
    opening_day = request.args.get('opening_day', '')
    city_filter = request.args.get('city', '')
    location_type = request.args.get('location_type', '')

    # Start with filtering only "active" locations
    query = Location.query.filter_by(status="active")

    # Apply filters
    if opening_day:
        day_column = getattr(Location, opening_day)
        query = query.filter(day_column.isnot(None))  # Check if the location is open that day

    if city_filter:
        city, country = city_filter.split('|')
        query = query.filter(Location.city == city, Location.country == country)

    if location_type:
        query = query.filter(Location.location_type == location_type)

    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(Location.location_rating.desc().nullslast())
    elif sort_order == 'asc':
        query = query.order_by(Location.location_rating.asc().nullsfirst())
    elif sort_order == 'seats_desc':
        query = query.order_by(Location.chairs.desc())
    elif sort_order == 'seats_asc':
        query = query.order_by(Location.chairs.asc())

    location_data = query.all()

    # Get available cities and location types for the filter options
    cities = db.session.query(Location.city, Location.country).distinct().all()
    location_types = db.session.query(Location.location_type).distinct().all()

    return render_template(
        'all-locations.html',
        location_data=location_data,
        cities=cities,
        location_types=location_types
    )


@main.route('/upload-location', methods=['GET', 'POST'])
@login_required
def upload_location():
    if request.method == 'POST':
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

        new_location = Location(user_id=current_user.id, location_name=location_name, location_type=location_type,
                                country=country, postal_code=postal_code, city=city, street=street, street_number=street_number,
                                chairs=chairs, monday_open=monday_open, monday_close=monday_close, tuesday_open=tuesday_open, tuesday_close=tuesday_close,
                                wednesday_open=wednesday_open, wednesday_close=wednesday_close, thursday_open=thursday_open, thursday_close=thursday_close,
                                friday_open=friday_open, friday_close=friday_close, saturday_open=saturday_open, saturday_close=saturday_close,
                                sunday_open=sunday_open, sunday_close=sunday_close, location_picture=location_picture)

        db.session.add(new_location)
        db.session.commit()

        flash("Your location has been successfully added.", "success")
        return redirect(url_for('main.main_page'))

    # Pass existing_location to the template
    existing_location = Location.query.filter_by(user_id=current_user.id).first()
    locations = Location.query.all()
    return render_template('upload-location.html', locations=locations, existing_location=existing_location)

@main.route('/make-reservation', methods=['GET', 'POST'])
@login_required
def make_reservation():
    if not current_user.is_authenticated:
        print("User is not authenticated!")
        return redirect(url_for('main.login'))  # Optional: Just in case

    if request.method == 'POST':
        # Get reservation details from the form
        reservation_time = request.form.get('reservation_time')
        number_of_guests = request.form.get('number_of_guests')
        study_time = request.form.get('study_time')

        # Validate and parse the reservation time
        try:
            reservation_datetime = datetime.strptime(reservation_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash('Invalid reservation time format. Please try again.', 'danger')
            return redirect(url_for('main.make_reservation'))

        # Filter locations based on availability
        available_locations = filter_available_locations(reservation_datetime, study_time, number_of_guests)

        # Pass the filtered locations to the location selection page
        return render_template(
            'select-location.html',
            location_data=available_locations,
            reservation_time=reservation_time,
            study_time=study_time,
            number_of_guests=number_of_guests,
        )

    # Render the reservation form
    return render_template('make-reservation.html')

@main.route('/select-location', methods=['GET', 'POST'])
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
        return redirect(url_for('main.make_reservation'))  # Stuur gebruiker terug naar het reserveringsformulier

    # Converteer en valideer de gegevens
    try:
        reservation_datetime = datetime.strptime(reservation_time, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Invalid reservation time format.", "error")
        return redirect(url_for('main.make_reservation'))

    try:
        study_time = int(study_time)
        number_of_guests = int(number_of_guests)
    except ValueError:
        flash("Study time and number of guests must be valid numbers.", "error")
        return redirect(url_for('main.make_reservation'))

    # Controleer of de reserveringsdatum in de toekomst ligt
    if reservation_datetime < datetime.now():
        flash("You can only make reservations for future dates and times.", "error")
        return redirect(url_for('main.make_reservation'))

    # Roep de functie aan om beschikbare locaties te filteren
    available_locations = filter_available_locations(reservation_datetime, study_time, number_of_guests)

    # Render de pagina met beschikbare locaties
    return render_template(
        'select-location.html',
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
    return redirect(url_for('main.main_page'))


def filter_available_locations(reservation_datetime, study_time, number_of_guests):
    """
    Helper function to filter locations based on reservation time, study time, and number of guests.
    This includes handling locations that are open past midnight (e.g., from 10 PM to 2 AM).
    It dynamically calculates available seats based on existing reservations.
    """
    # Ensure the study time is a valid positive integer
    try:
        study_time = int(study_time)
        if study_time <= 0:
            flash("Invalid study time.", "danger")
            return []
    except ValueError:
        flash("Study time must be a valid number.", "danger")
        return []

    # Define the end time of the reservation based on the study time
    reservation_end_time = reservation_datetime + timedelta(minutes=study_time)

    # Query locations that are active and have seating
    all_locations = Location.query.filter_by(status="active").all()
    available_locations = []

    for location in all_locations:
        # Calculate already reserved seats for this location and time slot
        existing_reservations = Reservation.query.filter(
            Reservation.location_id == location.id,
            Reservation.reservation_time < reservation_end_time,  # Reservation starts before end time
            Reservation.reservation_time + timedelta(minutes=study_time) > reservation_datetime  # Reservation ends after the requested start time
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
        return redirect(url_for('main.make_reservation'))

    # Retrieve the reservation
    reservation = Reservation.query.get_or_404(reservation_id)

    # Check if the current user owns the reservation
    if reservation.user_id != current_user.id:
        flash('You are not authorized to cancel this reservation.', 'error')
        return redirect(url_for('main.make_reservation'))

    # Update the status to "canceled"
    reservation.status = "canceled"
    db.session.commit()

    flash('Reservation successfully canceled.', 'success')
    return redirect(url_for('main.your_reservations'))


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))  # Redirect to login after logout

@main.route('/your-reservations', methods=['GET', 'POST'])
@login_required
def your_reservations():
    if request.method == 'POST':
        # Process location rating submission
        reservation_id = request.form.get('reservation_id')
        location_rating = request.form.get('location_rating')
        host_message = request.form.get('host_message')

        if reservation_id and location_rating:
            reservation = Reservation.query.get_or_404(reservation_id)

            # Ensure the user owns the reservation
            if reservation.user_id == current_user.id:
                try:
                    location_rating = int(location_rating)
                    if 1 <= location_rating <= 5:
                        reservation.location_rating = location_rating

                        # Save the host message if provided
                        if host_message:
                            reservation.host_message = host_message

                        db.session.commit()

                        # Update the location's average rating
                        update_location_rating(reservation.location_id)

                        flash("Your rating has been saved successfully!", "success")
                    else:
                        flash("Invalid rating value. Please select a value between 1 and 5.", "error")
                except ValueError:
                    flash("Invalid rating input. Please try again.", "error")
            else:
                flash("You are not authorized to rate this reservation.", "error")
        else:
            flash("Missing reservation ID or rating value.", "error")

        # Corrected url_for call
        return redirect(url_for('main.your_reservations'))

    # Fetch reservations
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
        'your-reservations.html', 
        reservations=active_reservations,
        expired_reservations=expired_reservations,
        user_rating=current_user.user_rating
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

@main.route('/your-bookings', methods=['GET', 'POST'])
@login_required
def your_bookings():
    if request.method == 'POST':
        # Process location rating submission
        reservation_id = request.form.get('reservation_id')
        student_rating = request.form.get('student_rating')
        student_message = request.form.get('student_message')

        if reservation_id and student_rating:
            reservation = Reservation.query.get_or_404(reservation_id)

            # Ensure the user owns the location
            if reservation.location and reservation.location.user_id == current_user.id:
                try:
                    student_rating = int(student_rating)
                    if 1 <= student_rating <= 5:
                        reservation.student_rating = student_rating

                        # Save the host message if provided
                        if student_message:
                            reservation.student_message = student_message

                        db.session.commit()

                        # Update the student's average rating
                        update_user_rating(reservation.user_id)

                        # Update the location owner's average rating
                        update_user_rating(reservation.location.user_id)

                        flash("Your rating has been saved successfully!", "success")
                    else:
                        flash("Invalid rating value. Please select a value between 1 and 5.", "error")
                except ValueError:
                    flash("Invalid rating input. Please try again.", "error")
            else:
                flash("You are not authorized to rate this reservation.", "error")
        else:
            flash("Missing reservation ID or rating value.", "error")

        return redirect(url_for('main.your_bookings'))

    # Fetch the active location of the current logged-in user
    location = Location.query.filter_by(user_id=current_user.id, status='active').first()

    if not location:
        flash('You do not own any active locations.', 'danger')
        return redirect(url_for('main.main_page'))

    # Get active reservations for this location
    reservations = Reservation.query.filter_by(location_id=location.id, status='active').all()

    # Get expired reservations for this location
    expired_reservations = Reservation.query.filter_by(location_id=location.id, status='expired').all()

    # Render the template, passing the location and reservations
    return render_template(
        'your-bookings.html',
        location=location, 
        reservations=reservations,
        expired_reservations=expired_reservations
        )

def update_user_rating(user_id):
    """ Calculate and update the average rating for a user. """
    # Calculate the average student rating
    avg_rating = (
        db.session.query(func.avg(Reservation.student_rating))
        .filter(Reservation.user_id == user_id, Reservation.student_rating.isnot(None))
        .scalar()
    )
    avg_rating = round(avg_rating) if avg_rating else None  # Round to the nearest integer or set to None

    # Update the user's `user_rating` in the database
    user = User.query.get(user_id)
    if user:
        user.user_rating = avg_rating
        db.session.commit()

    return avg_rating

def update_location_rating(location_id):
    """ Calculate and update the average rating for a location. """
    # Calculate the average location rating
    avg_rating = (
        db.session.query(func.avg(Reservation.location_rating))
        .filter(Reservation.location_id == location_id, Reservation.location_rating.isnot(None))
        .scalar()
    )
    avg_rating = round(avg_rating) if avg_rating else None  # Round to nearest integer or None

    # Update the location's average rating in the database
    location = Location.query.get(location_id)
    if location and avg_rating is not None:
        location.location_rating = avg_rating
        db.session.commit()

    return avg_rating

@main.route('/about')
def about():
    # Query the database to count expired reservations
    expired_reservations_count = Reservation.query.filter_by(status="expired").count()

    # Query the database to count locations
    location_count = Location.query.count()  # This assumes you have a Location model

    # Pass the counts to the template
    return render_template('about.html', expired_reservations_count=expired_reservations_count, location_count=location_count)