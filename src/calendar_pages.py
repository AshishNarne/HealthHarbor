from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import datetime
from .models import Reminder, Doctor, Patient
from . import db

bp = Blueprint("calendar_pages", __name__)

def build_month_str(date1: datetime.date, date2: datetime.date) -> str:
    month_str = date2.strftime("%b %Y")
    if date1.month != date2.month:
        fmat = "%b" if date1.year == date2.year else "%b %Y"
        month_str = f"{date1.strftime(fmat)} - " + month_str
    return month_str


def process_reminders(
    reminders: list[Reminder], monday: datetime.date
) -> list[list[Reminder]]:
    reminders.sort(key=lambda reminder: reminder.timestamp)
    reminders = filter(
        lambda reminder: datetime.timedelta(days=0)
        <= reminder.timestamp.date() - monday
        < datetime.timedelta(days=7),
        reminders,
    )
    reminders_by_weekday = [[] for _ in range(7)]
    for reminder in reminders:
        reminders_by_weekday[reminder.timestamp.weekday()].append(reminder)
    return reminders_by_weekday


@bp.route("/add-reminder")
@login_required
def add_reminder():
    if current_user.user_type != "doctor":
        return render_template("pages/forbidden.html"), 403
    return render_template("pages/add_reminder.html")


@bp.route("/add-reminder", methods=["POST"])
@login_required
def add_reminder_post():
    if current_user.user_type != "doctor":
        return render_template("pages/forbidden.html"), 403
    patient_id = request.form.get("patient")
    date = request.form.get("date")
    time = request.form.get("time")
    title = request.form.get("title")
    desc = request.form.get("desc")
    print(f"Adding reminder {patient_id, date, time, title, desc}")
    timestamp = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    print(timestamp)

    new_reminder = Reminder(
        timestamp=timestamp,
        title=title,
        desc=desc,
        doctor_id=current_user.id,
        patient_id=patient_id,
    )
    db.session.add(new_reminder)
    db.session.commit()
    return redirect(url_for("calendar_pages.calendar", week=0))


@bp.route("/calendar")
@login_required
def calendar():
    week = int(request.args.get("week", "0"))

    today = datetime.date.today()
    monday = (
        today
        - datetime.timedelta(days=today.weekday())
        + datetime.timedelta(weeks=week)
    )
    dates = [monday + datetime.timedelta(days=i) for i in range(7)]

    month_str = build_month_str(dates[0], dates[-1])
    reminders_by_weekday = process_reminders(current_user.reminders, monday)

    return render_template(
        "pages/calendar.html",
        reminders_by_weekday=reminders_by_weekday,
        dates=dates,
        month_str=month_str,
        week=week,
        patient=current_user.user_type == "patient",
    )


@bp.route("/delete-reminder", methods=["POST"])
@login_required
def delete_reminder():
    if current_user.user_type != "doctor":
        return render_template("pages/forbidden.html"), 403
    week = int(request.args.get("week"))
    reminder_id = int(request.args.get("reminder_id"))
    Reminder.query.filter_by(id=reminder_id).delete()
    db.session.commit()
    return redirect(url_for("calendar_pages.calendar", week=week))


@bp.route("/add-patient", methods=["GET", "POST"])
def add_patient():
    if current_user.user_type != "doctor":
        return render_template("pages/forbidden.html"), 403
    patients = []
    input_name = request.form.get("name")
    if input_name is not None:
        patients = Patient.query.filter(
            (Patient.fname + " " + Patient.lname).like(input_name + "%")
        ).all()
    return render_template("pages/add_patient.html", patients=patients)


@bp.route("/request-patient", methods=["POST"])
def request_patient():
    patient_id = int(request.form.get("patient_id"))
    doctor_id = int(request.form.get("doctor_id"))
    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)
    doctor.patients.append(patient)
    db.session.commit()
    return redirect(url_for("account_pages.home"))
