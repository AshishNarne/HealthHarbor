from email.message import EmailMessage
import ssl
import smtplib
from smtplib import SMTPRecipientsRefused


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
