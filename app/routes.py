from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, Location, Reservation
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
            login_user(user)
            flash('Login Successful!', 'success')
            return redirect(url_for('main.main_page'))
        else:
            flash('Invalid username or password, please try again.', 'error')
            return redirect(url_for('main.login'))
        
    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        student_id = request.form.get('studentID')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('main.signup'))

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, student_id=student_id, password_hash=password_hash)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.success'))

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
            monday_open=request.form.get("monday_open"),
            monday_close=request.form.get("monday_close"),
            tuesday_open=request.form.get("tuesday_open"),
            tuesday_close=request.form.get("tuesday_close"),
            wednesday_open=request.form.get("wednesday_open"),
            wednesday_close=request.form.get("wednesday_close"),
            thursday_open=request.form.get("thursday_open"),
            thursday_close=request.form.get("thursday_close"),
            friday_open=request.form.get("friday_open"),
            friday_close=request.form.get("friday_close"),
            saturday_open=request.form.get("saturday_open"),
            saturday_close=request.form.get("saturday_close"),
            sunday_open=request.form.get("sunday_open"),
            sunday_close=request.form.get("sunday_close"),
            location_picture=request.form.get("location_picture")
        )
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('main.success'))

    return render_template('locations.html')

@main.route('/reservations', methods=['GET', 'POST'])
@login_required
def reservations():
    locations = Location.query.all()
    user_reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('reservations.html', locations=locations, reservations=user_reservations)

@main.route('/make_reservation', methods=['POST'])
@login_required
def make_reservation():
    location_id = request.form['location_id']
    date = request.form['date']
    time = request.form['time']

    existing = Reservation.query.filter_by(location_id=location_id, date=date, time=time).first()
    if existing:
        flash('This time slot is already reserved!', 'error')
        return redirect(url_for('main.reservations'))

    new_reservation = Reservation(user_id=current_user.id, location_id=location_id, date=date, time=time)
    db.session.add(new_reservation)
    db.session.commit()

    flash('Reservation made successfully!', 'success')
    return redirect(url_for('main.reservations'))

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
