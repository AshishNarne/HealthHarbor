from flask import Blueprint, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Doctor, Patient
from . import db

bp = Blueprint("account_pages", __name__)


@bp.route("/")
def home():
    return render_template("pages/home.html")


@bp.route("/about")
def about():
    return render_template("pages/about.html")


@bp.route("/login")
def login():
    return render_template("pages/login.html")


@bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    pwd = request.form.get("pwd")
    remember = bool(request.form.get("remember"))

    user = User.query.filter_by(email=email).first()
    if not user:
        # maybe we shouldn't tell the user this
        flash("Not an existing email")
        return redirect(url_for("account_pages.login"))
    if not check_password_hash(user.pwd_hash, pwd):
        flash("Wrong password")
        return redirect(url_for("account_pages.login"))
    print(f"{user = } logging in")
    login_user(user, remember=remember)
    return render_template("pages/home.html")


@bp.route("/signup")
def signup():
    return render_template("pages/signup.html")


@bp.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    pwd = request.form.get("pwd")
    doctor = request.form.get("doctor")

    # look for an existing user
    user = User.query.filter_by(email=email).first()

    # if there is already a user with that email, don't allow creation of a new account, redirect to login page
    if user:
        login_url = url_for("account_pages.login")
        flash(
            Markup(f"User already exists, go to the <a href={login_url}>login page</a>")
        )
        return redirect(url_for("account_pages.signup"))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    user_type = Doctor if doctor else Patient
    new_user = user_type(
        email=email, fname=fname, lname=lname, pwd_hash=generate_password_hash(pwd)
    )

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=False)
    return redirect(url_for("account_pages.profile"))


@bp.route("/profile")
@login_required
def profile():
    return render_template("pages/profile.html", user=current_user)


@bp.route("/profile", methods=["POST"])
@login_required
def profile_post():
    user = current_user
    user.height = request.form.get("height")
    user.weight = request.form.get("weight")
    user.allergies = request.form.get("allergies")
    user.blood_type = request.form.get("blood_type")
    user.blood_pressure = request.form.get("blood_pressure")
    user.past_medicine = request.form.get("past_medicine")
    db.session.commit()
    return render_template(
        "pages/profile.html",
        user=current_user,
        height=user.height,
        weight=user.weight,
        allergies=user.allergies,
        blood_type=user.blood_type,
        blood_pressure=user.blood_pressure,
        past_medicine=user.past_medicine,
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("account_pages.home"))
