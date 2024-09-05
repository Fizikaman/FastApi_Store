from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Product(Base):
    __tablename__ = 'products'

    # fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    image_url = Column(String)
    rating = Column(Float)
    is_active = Column(Boolean, default=True)

    # relations
    category_id = Column(Integer, ForeignKey('categories.id'))
    supplier_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    category = relationship('Category', back_populates='products')
