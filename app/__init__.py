import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, jwt

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-prod')
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = False  # Set True in production with HTTPS
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Long-lived for simplicity

    # Database
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    # Fix postgres:// -> postgresql:// for SQLAlchemy
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register routes
    from app.routes import main
    app.register_blueprint(main)

    # Create tables
    with app.app_context():
        db.create_all()
        _create_default_admin()

    return app


def _create_default_admin():
    """Create a default admin user if none exists."""
    from app.models import User
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@ciphervault.com',
            password=generate_password_hash('Admin@123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
