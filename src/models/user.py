from flask_login import UserMixin
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from constants import DEFAULT_LEND_DURATION

from models.database import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[String] = mapped_column(String(250), nullable=False)
    last_name: Mapped[String] = mapped_column(String(250), nullable=False)
    email: Mapped[String] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[String] = mapped_column(String(250), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_LEND_DURATION)
    my_books = Relationship('Book', foreign_keys='Book.owner_id', back_populates='book_owner')
    reserved_books = Relationship('Book', foreign_keys='Book.lender_id', back_populates='book_lender')

    def get_user_dict(self):
        return {
            "id": self.id,
            "name": self.first_name,
            "email": self.email,
            "duration": self.duration
        }
