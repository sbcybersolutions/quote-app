import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Build absolute path to quotes.db
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(basedir, ".."))
    db_path = os.path.join(project_root, "quotes.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)

    # Create tables
    with app.app_context():
        from .models import Quote  # ensure model is registered
        db.create_all()

    # Initialize Flask-Admin with Bootstrap 3 templates
    admin = Admin(app, name="Quotes Admin", template_mode="bootstrap3")
    from .models import Quote
    admin.add_view(ModelView(Quote, db.session))

    # Register your main blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
