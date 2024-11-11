from flask import Flask # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # Load the config settings

db = SQLAlchemy(app)  # Initialize SQLAlchemy with your app

@app.route('/')
def home():
    return "Hello world..."
@app.route('/register')
def register():
    return "Register: Name and Password"

@app.route('/login')
def login():
    return "Login : Name and Password"

@app.route('/products')
def products():
    return "Chairing"


if __name__ == "__main__":
    app.run(debug=True)  # Run the app in debug mode

