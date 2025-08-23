from datetime import date

from sqlalchemy import Integer, String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import db


class Book(db.Model):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[String] = mapped_column(String(250), nullable=False, unique=True)
    author: Mapped[String] = mapped_column(String(250), nullable=False)
    description: Mapped[String] = mapped_column(String(4000))
    image_url: Mapped[String] = mapped_column(String(250), nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    reserved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lent_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    lender_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=True)
    book_owner = relationship('User', foreign_keys=[owner_id], back_populates='my_books')
    book_lender = relationship('User', foreign_keys=[lender_id], back_populates='reserved_books')

    def to_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'img': self.image_url,
            'reserved': self.reserved,
            'lentOut': self.lent_out,
            'isActive': self.active,
            'ownerId': self.owner_id,
            'lenderId': self.lender_id,
            'returnDate': self.return_date
        }

        if self.return_date and self.return_date < date.today():
            result['overdue'] = True
        return result
