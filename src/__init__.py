from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()
load_dotenv()

from . import pages

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(pages.bp)

    return app