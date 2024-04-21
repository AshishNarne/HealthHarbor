from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager
import atexit
from flask_apscheduler import APScheduler

db = SQLAlchemy()

from . import account_pages
from . import calendar_pages
from .models import User
from .email import send_email_notifications


def create_app():
    app = Flask(__name__)
    app.register_blueprint(account_pages.bp)
    app.register_blueprint(calendar_pages.bp)

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
    login_manager.login_view = "account_pages.login"
    login_manager.init_app(app)

    scheduler = APScheduler()
    scheduler.init_app(app)
    account = app.config["GMAIL_ACCOUNT"]
    password = app.config["GMAIL_PASSWORD"]
    scheduler.add_job(
        id="send-email-notifications",
        func=lambda: send_email_notifications(account, password, app),
        trigger="interval",
        seconds=60,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    @login_manager.user_loader
    def load_user(user_id):
        print(f"{user_id = }")
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    return app
