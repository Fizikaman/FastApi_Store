from datetime import datetime

from pydantic import BaseModel


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class CreateReview(BaseModel):
    comment: str | None = None
    grade: int


class GetAllReviews(BaseModel):
    id: int
    comment: str | None = None
    comment_date: datetime
    user_id: int
    user_name: str
    product_name: str
    grade: int

    class Config:
        from_attributes = True
