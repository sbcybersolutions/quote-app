import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    # Initialize Flask app
    app = Flask(__name__, instance_relative_config=False)
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Build absolute path to quotes.db in the project root
    # __file__ is app/__init__.py, so go up one level to project root
    basedir = os.path.abspath(os.path.dirname(__file__))      # .../quote_app/app
    project_root = os.path.abspath(os.path.join(basedir, ".."))
    db_path = os.path.join(project_root, "quotes.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Create tables
    with app.app_context():
        # Import models so they’re registered with SQLAlchemy
        from .models import Quote  # noqa: F401
        db.create_all()
        # You can add a debug print to confirm:
        print(f"Database file path: {db_path}")

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
