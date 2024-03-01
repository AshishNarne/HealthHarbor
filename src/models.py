from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column
from . import db

class User(UserMixin, db.Model):
    # id is just an autoincrementing(?) integer (1, 2, 3, ...) that uniquely identifies a user
    id: Mapped[int] = mapped_column(primary_key=True)
    # unique makes it so that no two accounts can have the same email
    email: Mapped[str] = mapped_column(unique=True)
    fname: Mapped[str] = mapped_column()
    lname: Mapped[str] = mapped_column()
    pwd_hash: Mapped[str] = mapped_column()
    
class Reminder(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
