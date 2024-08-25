from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, select, update
from app.schema import CreateCategory, CreateProduct

from slugify import slugify

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    if products:
        return products
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No products found')


@router.post('/create')
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct) -> dict:
    await db.execute(insert(Product).values(
        name=create_product.name,
        slug=slugify(create_product.name),
        description=create_product.description,
        price=create_product.price,
        stock=create_product.stock,
        image_url=create_product.image_url,
        rating=0.0,
        category_id=create_product.category
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }



@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))

    category_ids = [category.id] + [subcat.id for subcat in subcategories.all()]
    products = await db.scalars(
        select(Product)
        .where(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.stock > 0
        )
    )

    return products.all()


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[Session, Depends(get_db)],
                         update_product: CreateProduct, product_slug: str) -> dict:
    product = await db.scalar(select(Category).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    await db.execute(update(Product).where(Product.slug == product_slug).values(
        name=update_product.name,
        slug=slugify(update_product.name),
        description=update_product.description,
        price=update_product.price,
        stock=update_product.stock,
        image_url=update_product.image_url,
        category_id=update_product.category
    ))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product updated'
    }


@router.delete('/delete')
async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str) -> dict:
    product = await db.scalar(select(Category).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product does not exist'
        )
    await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_204_NO_CONTENT,
        'transaction': 'Category deleted'
    }