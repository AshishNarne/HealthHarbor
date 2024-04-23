from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Doctor, Patient, Reminder, DoctorPatient, Message
from . import db
from .email import send_email

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


@bp.route("/verify_email")
def verify_email():
    return render_template("pages/verify_email.html")


@bp.route("/verify_email", methods=["POST"])
def verify_email_post():
    email = request.form.get("email")
    session["email"] = email

    user = User.query.filter_by(email=email).first()
    if not user:
        # maybe we shouldn't tell the user this
        flash("Not an existing email")
        return redirect(url_for("account_pages.verify_email"))

    return redirect(url_for("account_pages.change_password", email=email))


@bp.route("/change_password")
def change_password():
    return render_template("pages/change_password.html")


@bp.route("/change_password", methods=["POST"])
def change_password_post():
    email = session.get("email")
    pwd = request.form.get("pwd")

    user = User.query.filter_by(email=email).first()
    user.pwd_hash = generate_password_hash(pwd)
    db.session.commit()

    return redirect(url_for("account_pages.login"))


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

    if not send_email(
        current_app.config["GMAIL_ACCOUNT"],
        current_app.config["GMAIL_PASSWORD"],
        email,
        "Welcome to HealthHarbor!",
        "Thanks for signing up to HealthHarbor.",
    ):
        flash("Enter a valid email")
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
    print(f"form: {request.form}")
    if "delete-account-submit" in request.form:
        user_id = current_user.id
        logout_user()
        patient_exists = Patient.query.filter_by(id=user_id).first()
        User.query.filter_by(id=user_id).delete()
        if patient_exists:
            Patient.query.filter_by(id=user_id).delete()
            Reminder.query.filter_by(patient_id=user_id).delete()
            DoctorPatient.query.filter_by(patient_id=user_id).delete()
        else:
            Doctor.query.filter_by(id=user_id).delete()
            Reminder.query.filter_by(doctor_id=user_id).delete()
            DoctorPatient.query.filter_by(doctor_id=user_id).delete()
        db.session.commit()
        return redirect(url_for("account_pages.home"))
    else:
        # display the user's medical details
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


@bp.route("/direct-messages", methods=["GET", "POST"])
@login_required
def direct_messages():
    other_id = request.form.get("dm-user-select")
    if other_id is not None:
        other_id = int(other_id)
    if "send-dm-input" in request.form:
        other_id = int(request.form.get("other-user-id"))
        new_dm_content = request.form.get("send-dm-input")
        new_message = Message(
            from_id=current_user.id, to_id=other_id, content=new_dm_content
        )
        db.session.add(new_message)
        db.session.commit()
    other_user = None
    messages = []
    # other_users will store all the users the current user could direct message
    other_users = []
    if current_user.user_type == "patient":
        other_users = current_user.doctors
    else:
        other_users = current_user.patients
    if other_id is not None:
        other_id = int(other_id)
        user_id = current_user.id
        other_user = User.query.filter_by(id=other_id).first()
        # filter all messages that should be on screen
        # so either from current user to other user or vice-versa
        messages = Message.query.filter(
            ((Message.from_id == user_id) & (Message.to_id == other_id))
            | ((Message.from_id == other_id) & (Message.to_id == user_id))
        )
    return render_template(
        "pages/direct_messages.html",
        user=current_user,
        dm_other=other_user,
        messages=messages,
        other_users=other_users,
    )
