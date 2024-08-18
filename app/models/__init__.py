from sqlalchemy.schema import CreateTable

from app.models.products import Product
from app.models.category import Category


print(CreateTable(Product.__table__))
print(CreateTable(Category.__table__))
