from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access EDRLite.'
login_manager.login_message_category = 'warning'


def init_db(app):
    """Initialise SQLAlchemy and create all tables."""
    db.init_app(app)
    with app.app_context():
        from database.models import (  # noqa: F401
            Endpoint, RawEvent, Alert, MitreEvent, RiskScore
        )
        db.create_all()
