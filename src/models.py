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
    reminders: Mapped[list['Reminder']] = relationship(back_populates='user')
    height: Mapped[str] = mapped_column()
    weight: Mapped[str] = mapped_column()
    allergies: Mapped[str] = mapped_column()
    blood_type: Mapped[str] = mapped_column()
    blood_pressure: Mapped[str] = mapped_column()
    past_medicine: Mapped[str] = mapped_column()
    
class Reminder(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship(back_populates='reminders')
    timestamp: Mapped[datetime] = mapped_column()
    title: Mapped[str] = mapped_column()
    desc: Mapped[str] = mapped_column()
