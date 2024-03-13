from flask_login import UserMixin
from datetime import datetime
from enum import Enum, auto
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
    reminders: Mapped[list['Reminder']] = relationship(back_populates='user')
    __mapper_args__ = {
        'polymorphic_identity': 'employee',
        'polymorphic_on': 'user_type',
    }


class Doctor(User):
    id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    patients: Mapped[list['Patient']] = relationship(back_populates='doctor', foreign_keys='Patient.doctor_id')
    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
    }


class Patient(User):
    id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('doctor.id'))
    doctor: Mapped['Doctor'] = relationship(back_populates='patients', foreign_keys='Patient.doctor_id')
    __mapper_args__ = {
        'polymorphic_identity': 'patient',
    }


class Reminder(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='reminders')
    timestamp: Mapped[datetime] = mapped_column()
    title: Mapped[str] = mapped_column()
    desc: Mapped[str] = mapped_column()
    
