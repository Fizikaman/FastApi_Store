from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Review(Base):
    """Модель для хранения отзывов"""
    __tablename__ = 'reviews'

    # fields
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    comment = Column(String)
    comment_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # relations
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('ratings.id'))

    product = relationship('Product', back_populates='reviews')
    rating = relationship('Rating', back_populates='review')


class Rating(Base):
    __tablename__ = 'ratings'

    # fields
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)

    # relations
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    review = relationship('Review', back_populates='rating')
