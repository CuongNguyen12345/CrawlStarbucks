# from CrawlStarbucks.services.data_service import get_all_drinks_from_db
from flask import request
from CrawlStarbucks.db.database import SessionLocal
from CrawlStarbucks.models import Drink, DrinkInfo, Category
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased

def get_all_drinks():
    session = SessionLocal()
    type_id = request.args.get("type")

    subq = (
        session.query(
            DrinkInfo.drink_id.label("drink_id"),
            func.min(DrinkInfo.size_id).label("min_size_id")
        )
        .group_by(DrinkInfo.drink_id)
        .subquery()
    )

    InfoAlias = aliased(DrinkInfo)

    query = (
        session.query(Drink, InfoAlias)
        .join(subq, subq.c.drink_id == Drink.id)
        .join(InfoAlias, and_(
            InfoAlias.drink_id == subq.c.drink_id,
            InfoAlias.size_id == subq.c.min_size_id
        ))
    )

    if type_id:
        query = query.filter(Drink.category_id == type_id)

    results = (
        query.all()
    )

    drinks = []
    for drink, drink_info in results:
        drinks.append({
            "id": drink.id,
            "name": drink.name,
            "image_url": drink.image_url,
            "calories": drink_info.calories,
            "sugars": drink_info.sugars,
            "caffeine": drink_info.caffeine
        })
    return drinks

def get_single_drink(drink_id):
    session = SessionLocal()
    return session.query(Drink, DrinkInfo, Category) \
        .join(DrinkInfo, Drink.id == DrinkInfo.drink_id) \
        .join(Category, Drink.category_id == Category.id) \
        .filter(Drink.id == drink_id) \
        .first()

def get_all_categories():
    session = SessionLocal()
    categories = session.query(Category).filter(Category.parent_id != None).all()

    return categories