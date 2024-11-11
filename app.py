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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

#@app.route('/products')
#def products():
    #return "Chairing"

if __name__ == "__main__":
    app.run(debug=True)  # Run the app in debug mode

