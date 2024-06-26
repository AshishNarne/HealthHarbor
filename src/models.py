from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db


class User(UserMixin, db.Model):
    # id is just an autoincrementing(?) integer (1, 2, 3, ...) that uniquely identifies a user
    id: Mapped[int] = mapped_column(primary_key=True)
    # unique makes it so that no two accounts can have the same email
    email: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str] = mapped_column()
    lname: Mapped[str] = mapped_column()
    pwd_hash: Mapped[str] = mapped_column()
    user_type: Mapped[str] = mapped_column()
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "user_type",
    }


# model for connection between doctor and patient
# necessary since this is a many-to-many relationship
class DoctorPatient(db.Model):
    __tablename__ = "doctor_patient"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"))


class Doctor(User):
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    patients: Mapped[list["Patient"]] = relationship(
        secondary="doctor_patient", back_populates="doctors"
    )
    __mapper_args__ = {
        "polymorphic_identity": "doctor",
    }
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="doctor")


class Patient(User):
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    doctors: Mapped[list["Doctor"]] = relationship(
        secondary="doctor_patient", back_populates="patients"
    )
    __mapper_args__ = {
        "polymorphic_identity": "patient",
    }
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="patient")

    height: Mapped[str] = mapped_column(nullable=True)
    weight: Mapped[str] = mapped_column(nullable=True)
    allergies: Mapped[str] = mapped_column(nullable=True)
    blood_type: Mapped[str] = mapped_column(nullable=True)
    blood_pressure: Mapped[str] = mapped_column(nullable=True)
    past_medicine: Mapped[str] = mapped_column(nullable=True)


class Reminder(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"))
    patient: Mapped["Patient"] = relationship(back_populates="reminders")
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"))
    doctor: Mapped["Doctor"] = relationship(back_populates="reminders")
    timestamp: Mapped[datetime] = mapped_column()
    title: Mapped[str] = mapped_column()
    desc: Mapped[str] = mapped_column()
    email_sent: Mapped[str] = mapped_column()


# model for a single direct message
class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    to_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    content: Mapped[str] = mapped_column()
