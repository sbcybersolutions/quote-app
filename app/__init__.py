import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Initialize the database
db = SQLAlchemy()

def create_app():
    from app.models import ProjectType, Resource, Quote, QuoteItem

    # Update QuoteItem total_cost calculation
    QuoteItem.total_cost = property(lambda self: (self.unit_cost / 0.5) * self.quantity)  # type: ignore

    class ResourceAdmin(ModelView):
        form_columns = ['name', 'hours_per_unit', 'rate_per_hour', 'project_type']
        column_filters = ['project_type']
        form_args = {
            'project_type': {
                'query_factory': lambda: ProjectType.query,
                'allow_blank': False
            }
        }

    app = Flask(__name__, instance_relative_config=False)
    app.config['SECRET_KEY'] = 'your-secret-key'

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.abspath(os.path.join(basedir, '..')), 'quotes.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Delayed import to prevent circular import
        from app.models import VideoType

        if not VideoType.query.first():
            video_types = [
                ("Explainer Video", 20.00),
                ("Promo Video", 25.00),
                ("Internal Training", 18.00),
                ("Product Walkthrough", 22.00),
                ("Compliance Video", 17.00),
                ("Bespoke Course Video", 30.00),
                ("Animated Overview", 28.00),
            ]
            for name, rate in video_types:
                db.session.add(VideoType(name=name, cost_per_second=rate)) # type: ignore
            db.session.commit()

    admin = Admin(app, name='Quote Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(ProjectType, db.session))
    admin.add_view(ResourceAdmin(Resource, db.session))
    admin.add_view(ModelView(Quote, db.session))
    admin.add_view(ModelView(QuoteItem, db.session))
    admin.add_view(ModelView(VideoType, db.session))

    from app.routes import main as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app