## This file initializes the Flask application
## It loads configuration settings
## It initializes the database

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

# Initialize the database
db = SQLAlchemy()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # Load configuration from Config class

    # Initialize the database with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints (import the routes and register them as a blueprint)
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
