from email.message import EmailMessage
import ssl
import smtplib
from smtplib import SMTPRecipientsRefused
import datetime
from flask import current_app
from .models import Reminder
from . import db


def send_email(send: str, password: str, receive: str, subject: str, body: str) -> bool:
    em = EmailMessage()
    em["From"] = send
    em["To"] = receive
    em["Subject"] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(send, password)
        try:
            smtp.sendmail(send, receive, em.as_string())
        except SMTPRecipientsRefused:
            return False
        else:
            return True


def send_email_notifications(send: str, password: str, app):
    with app.app_context():
        reminders = Reminder.query.filter(
            (Reminder.email_sent == False)
            & (Reminder.timestamp < datetime.datetime.now())
        ).all()
        for reminder in reminders:
            send_email(
                send,
                password,
                reminder.patient.email,
                "You have an upcoming appointment",
                f"You have an appointment on {reminder.timestamp.strftime('%B %d at %I:%M %p')}."
                f"\nTitle: {reminder.title}"
                f"\nDescription: {reminder.desc}",
            )
            reminder.email_sent = True
        db.session.commit()
