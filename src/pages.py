from flask import Blueprint, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
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
    email = request.form.get('email')
    pwd = request.form.get('pwd')
    remember = bool(request.form.get('remember'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        print('Not an existing email')
        return redirect(url_for('pages.login'))
    if not check_password_hash(user.pwd_hash, pwd):
        print('Wrong password')
        return redirect(url_for('pages.login'))
    print(f'{user = }')
    login_user(user, remember=remember)
    return render_template('pages/home.html')

@bp.route('/signup')
def signup():
    return render_template('pages/signup.html')

@bp.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    pwd = request.form.get('pwd')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        login_url = url_for('pages.login')
        flash(Markup(f'User already exists, go to the <a href={login_url}>login page</a>'))
        return redirect(url_for('pages.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, fname=fname, lname=lname, pwd_hash=generate_password_hash(pwd))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=False)
    return redirect(url_for('pages.profile'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('pages/profile.html', user=current_user)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.home'))