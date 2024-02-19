from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager

db = SQLAlchemy()
load_dotenv()

from . import pages

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'pages.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        print(f'{user_id = }')
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    app.register_blueprint(pages.bp)

    return app