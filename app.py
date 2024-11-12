from flask import Flask, render_template, url_for, request, redirect # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)  # Load the config settings
#db = SQLAlchemy(app)  # Initialize SQLAlchemy with your app

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # You would add logic here to handle storing the new user in the database
        # and any other signup processing
        return redirect(url_for('main'))  # Redirect to success page after signup
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # You would add logic here to handle storing the new user in the database
        # and any other signup processing
        return redirect(url_for('success'))  # Redirect to success page after signup
    return render_template('signup.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/locations')
def locations():
    return render_template('locations.html')

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

if __name__ == "__main__":
    app.run(debug=True)  # Run the app in debug mode

