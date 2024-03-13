from flask import Blueprint, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import datetime
from .models import User, Reminder
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
        # maybe we shouldn't tell the user this
        flash('Not an existing email')
        return redirect(url_for('pages.login'))
    if not check_password_hash(user.pwd_hash, pwd):
        flash('Wrong password')
        return redirect(url_for('pages.login'))
    print(f'{user = } logging in')
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

    # look for an existing user
    user = User.query.filter_by(email=email).first()

    # if there is already a user with that email, don't allow creation of a new account, redirect to login page
    if user: 
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

def build_month_str(date1: datetime.date, date2: datetime.date) -> str:
    month_str = date2.strftime('%b %Y')
    if date1.month != date2.month:
        fmat = '%b' if date1.year == date2.year else '%b %Y'
        month_str = f'{date1.strftime(fmat)} - ' + month_str
    return month_str

def process_reminders(reminders: list[Reminder], monday: datetime.date) -> list[list[Reminder]]:
    reminders.sort(key=lambda reminder: reminder.timestamp)
    reminders = filter(
        lambda reminder: 
            datetime.timedelta(days=0) <= reminder.timestamp.date() - monday < datetime.timedelta(days=7),
        reminders
    )
    reminders_by_weekday = [[] for _ in range(7)]
    for reminder in reminders:
        reminders_by_weekday[reminder.timestamp.weekday()].append(reminder)
    return reminders_by_weekday

@bp.route('/calendar')
@login_required
def calendar():
    week = int(request.args.get('week', '0'))
    
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=week)
    dates = [monday + datetime.timedelta(days=i) for i in range(7)]
    
    month_str = build_month_str(dates[0], dates[-1])
    reminders_by_weekday = process_reminders(current_user.reminders, monday)

    return render_template('pages/calendar.html', reminders_by_weekday=reminders_by_weekday, dates=dates, month_str=month_str, week=week)

@bp.route('/calendar', methods=['POST'])
@login_required
def calendar_post():
    date = request.form.get('date')
    time = request.form.get('time')
    title = request.form.get('title')
    desc = request.form.get('desc')
    print(f'Adding reminder {date, time, title, desc}')
    timestamp = datetime.datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
    print(timestamp)
    
    new_reminder = Reminder(timestamp=timestamp, title=title, desc=desc, user_id=current_user.id)
    db.session.add(new_reminder)
    db.session.commit()

    return redirect(url_for('pages.calendar'))

@bp.route('/delete-reminder', methods=['POST'])
def delete_reminder():
    week = int(request.args.get('week'))
    reminder_id = int(request.args.get('reminder_id'))
    Reminder.query.filter_by(id=reminder_id).delete()
    db.session.commit()
    return redirect(url_for('pages.calendar', week=week))
