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
        email_sent=False,
    )
    db.session.add(new_reminder)
    db.session.commit()
    return redirect(url_for("calendar_pages.calendar", week=0))


@bp.route("/add-repeating-reminder")
@login_required
def add_repeating_reminder():
    if current_user.user_type != "doctor":
        return render_template("pages/forbidden.html"), 403
    return render_template("pages/add_repeating_reminder.html")


def create_repeating_reminder(desired_days, end_date, title, desc, patient_id, time):
    today = datetime.date.today()
    this_monday = today - datetime.timedelta(days=today.weekday())
    this_monday = datetime.datetime(
        this_monday.year, this_monday.month, this_monday.day
    )
    week = 0
    while True:
        # iterate through all the weekdays someone wants a reminder
        for desired_day in desired_days:
            reminder_datetime = this_monday + datetime.timedelta(
                weeks=week, days=desired_day, hours=time.hour, minutes=time.minute
            )
            if reminder_datetime < datetime.datetime.now():
                continue
            # if current day is past their desired end date, stop
            if reminder_datetime > end_date + datetime.timedelta(days=1):
                return
            new_reminder = Reminder(
                timestamp=reminder_datetime,
                title=title,
                desc=desc,
                doctor_id=current_user.id,
                patient_id=patient_id,
                email_sent=False,
            )
            db.session.add(new_reminder)
        week += 1


@bp.route("/add-repeating-reminder", methods=["POST"])
@login_required
def add_repeating_reminder_post():
    if current_user.user_type != "doctor":
        return render_template("pages/forbidden.html"), 403
    patient_id = request.form.get("patient")
    end_date = datetime.datetime.strptime(request.form.get("date"), "%Y-%m-%d")
    desired_days = []
    for i, weekday in enumerate(["m", "t", "w", "r", "f", "s", "u"]):
        if request.form.get(weekday):
            desired_days.append(i)
    print(f"{desired_days = }")
    time = datetime.datetime.strptime(request.form.get("time"), "%H:%M")
    title = request.form.get("title")
    desc = request.form.get("desc")
    create_repeating_reminder(desired_days, end_date, title, desc, patient_id, time)
    db.session.commit()
    return redirect(url_for("calendar_pages.calendar"))


@bp.route("/calendar")
@login_required
def calendar():
    week = int(request.args.get("week", "0"))

    today = datetime.date.today()
    # calculate the first day that should be displayed in the calendar
    # week variable controls which week is displayed
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
    # patients are forbidden from deleting reminders
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
        # patients are forbidden from adding other patients
        return render_template("pages/forbidden.html"), 403
    patients = []
    input_name = request.form.get("name")
    if input_name is not None:
        # find all patients with a similar name to the input query
        patients = Patient.query.filter(
            (Patient.fname + " " + Patient.lname).like(input_name + "%")
        ).all()
    return render_template("pages/add_patient.html", patients=patients)


@bp.route("/request-patient", methods=["POST"])
def request_patient():
    # add patient to a doctor's "network"
    patient_id = int(request.form.get("patient_id"))
    doctor_id = int(request.form.get("doctor_id"))
    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)
    doctor.patients.append(patient)
    db.session.commit()
    return redirect(url_for("account_pages.home"))
