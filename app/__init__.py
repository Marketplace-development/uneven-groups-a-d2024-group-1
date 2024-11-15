## This file initializes the Flask application
## It loads configuration settings
## It initializes the database

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize the database
db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # Load configuration from Config class

    # Initialize the database with the app
    db.init_app(app)
    login_manager.init_app(app) # Binds the login_manager to the app
    migrate.init_app(app, db)

    # Set the login_view for the LoginManager
    login_manager.login_view = "main.login" # Make sure this points to the login route

    # Register blueprints (import the routes and register them as a blueprint)
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# Add the user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))