import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize the database
db = SQLAlchemy()

# Import the model before using in lambda
def create_app():
    from app.models import ProjectType, Resource, Quote, QuoteItem

    # Custom admin view for Resource (defined inside create_app)
    class ResourceAdmin(ModelView):
        form_columns = ['name', 'hours_per_unit', 'rate_per_hour', 'project_type']
        form_args = {
            'project_type': {
                'query_factory': lambda: ProjectType.query,
                'allow_blank': False
            }
        }

    app = Flask(__name__, instance_relative_config=False)
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Absolute path to SQLite DB
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.abspath(os.path.join(basedir, '..')), 'quotes.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init DB
    db.init_app(app)

    # Import models before creating tables
    with app.app_context():
        db.create_all()

    # Set up admin interface
    admin = Admin(app, name='Quote Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(ProjectType, db.session))
    admin.add_view(ResourceAdmin(Resource, db.session))
    admin.add_view(ModelView(Quote, db.session))
    admin.add_view(ModelView(QuoteItem, db.session))

    # Register blueprint with modular routes
    from app.routes import main as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app
