from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Product, User, review
from app.models.review import Review, Rating
from app.routers.auth import get_current_user
from app.schema import CreateReview, GetAllReviews, GetAllProductsReviews

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/all_reviews', response_model=list[GetAllReviews])
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    """Получение всех отзывов о всех товарах"""
    result = await db.execute(select(Review.id,
                               Review.comment,
                               Review.comment_date,
                               Review.user_id,
                               User.username.label('username'),
                               Product.name.label('name'),
                               Rating.grade.label('grade')
                               ).join(Product, Review.product_id == Product.id)
                                .join(User, Review.user_id == User.id)
                                .join(Rating, Review.product_id == Product.id))
    reviews = result.all()

    all_reviews = [
        GetAllReviews(
            id=review.id,
            comment=review.comment,
            comment_date=review.comment_date,
            user_id=review.user_id,
            user_name=review.user_name,
            product_name=review.product_name,
            grade=review.grade
        ) for review in reviews
    ]

    return all_reviews


@router.get('/products/{product_slug}/reviews', response_model=list[GetAllProductsReviews])
async def create_review(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    """Метод получения всех отзывов по определенному товару"""
    product = db.scalar(select(Product.id).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Товар с {product_slug} не найден')

    result = await db.execute(select(Review.id,
                                     Review.comment,
                                     Review.comment_date,
                                     Review.user_id,
                                     User.username.label('username'),
                                     Rating.grade.label('grade')
                                     ).join(User, Review.user_id == User.id)
                              .join(Rating, Review.product_id == Product.id).where(Review.product_id == product.id))
    reviews = result.all()

    all_product_reviews = [
        GetAllProductsReviews(
            id=item.id,
            comment=item.comment,
            comment_date=item.comment_date,
            user_id=item.user_id,
            user_name=item.user_name,
            grade=item.grade
        ) for item in reviews
    ]

    return all_product_reviews


@router.post('/products/{product_slug}/reviews')
async def create_review(db: Annotated[AsyncSession, Depends(get_db)],
                        get_user: Annotated[dict, Depends(get_current_user)],
                        product_slug: str,
                        review_data: CreateReview):
    """Метод для создания отзыва и оценки товара"""
    if not get_user:
        raise HTTPException(detail='Требуется авторизация', status_code=status.HTTP_401_UNAUTHORIZED)

    if review_data.grade < 1 or review_data.grade > 5:
        raise HTTPException(detail='Оценка должна быть от 1 до 5', status_code=status.HTTP_400_BAD_REQUEST)

    async with db.begin():
        try:
            product = await db.scalar(select(Product).where(Product.slug == product_slug))

            if not product:
                raise HTTPException(detail='Товар не найден', status_code=status.HTTP_404_NOT_FOUND)

            existing_review = db.scalar(select(Review).where(Review.product == product,
                                                             Review.user_id == get_user.get('id')))

            if existing_review:
                raise HTTPException(detail='Вы уже оставляли отзыв на этот товар',
                                    status_code=status.HTTP_400_BAD_REQUEST)

            new_rating = Rating(grade=review_data.grade,
                                user_id=get_user.get('id'),
                                product_id=product.id)
            db.add(new_rating)
            await db.flush()

            new_review = Review(comment=review_data.comment,
                                user_id=get_user.get('id'),
                                product_id=product.id,
                                rating_id=new_rating.id)

            db.add(new_review)
            await db.flush()

            avg_rating = await db.scalar(select(func.avg(Rating.grade)).where(Rating.product_id == product.id,
                                                                              Rating.is_active == True))

            product.rating = round(avg_rating, 1)

            await db.commit()

        except Exception as e:
            await db.rollback()
            raise HTTPException(detail=f'Произошла ошибка {e}',
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return {"message": "Отзыв успешно добавлен", "new_rating": product.rating}
