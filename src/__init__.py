from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager

db = SQLAlchemy()

from . import pages
from .models import User, Reminder

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages.bp)
    
    # .env
    # import environment variables
    load_dotenv()
    app.config.from_prefixed_env()

    # db
    db.init_app(app)
    # creates all models and tables
    with app.app_context():
        db.create_all()

    # flask-login
    login_manager = LoginManager()
    login_manager.login_view = 'pages.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        print(f'{user_id = }')
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    return app