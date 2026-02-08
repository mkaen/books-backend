from datetime import date

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
from flask_login import UserMixin

from src.constants import DEFAULT_LEND_DURATION
from src.db.dao import db


class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, unique=True)
    author = Column(String(250), nullable=False)
    description = Column(String(4000))
    image_url = Column(String(250), nullable=False)
    return_date = Column(Date, default=None)
    reserved = Column(Boolean, nullable=False, default=False)
    lent_out = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner_id: Mapped[Integer] = Column(Integer, ForeignKey('users.id'), nullable=False)
    lender_id: Mapped[Integer] = Column(Integer, ForeignKey('users.id'))
    book_owner = relationship('User', foreign_keys=[owner_id], back_populates='my_books')
    book_lender = relationship('User', foreign_keys=[lender_id], back_populates='reserved_books')

    def to_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'image_url': self.image_url,
            'reserved': self.reserved,
            'lentOut': self.lent_out,
            'isActive': self.active,
            'ownerId': self.owner_id,
            'lenderId': self.lender_id,
            'returnDate': self.return_date,
            'overdue': False
        }

        if self.return_date and self.return_date < date.today():
            result['overdue'] = True
        return result


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    duration = Column(Integer, nullable=False, server_default=str(DEFAULT_LEND_DURATION))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    my_books: Mapped[list[Book]] = relationship('Book', foreign_keys="[Book.owner_id]")
    reserved_books: Mapped[list[Book]] = relationship('Book',
                                                      back_populates="book_lender",
                                                      foreign_keys="[Book.lender_id]")

    def get_user_dict(self):
        return {
            "id": self.id,
            "name": self.first_name,
            "email": self.email,
            "duration": self.duration
        }
