from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

bp = Blueprint('pages', __name__)

@bp.route('/')
def home():
    return render_template('pages/home.html')

@bp.route('/about')
def about():
    return render_template('pages/about.html')

@bp.route('/login')
def login():
    return render_template('pages/login.html')

@bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    pwd = request.form.get('pwd')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        print('Not a username')
        return redirect(url_for('pages.login'))
    if not check_password_hash(user.pwd, pwd):
        print('Wrong password')
        return redirect(url_for('pages.login'))
    return render_template('pages/home.html')

@bp.route('/signup')
def signup():
    return render_template('pages/signup.html')

@bp.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    username = request.form.get('username')
    pwd = request.form.get('pwd')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('pages.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, username=username, pwd=generate_password_hash(pwd))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('pages.login'))
