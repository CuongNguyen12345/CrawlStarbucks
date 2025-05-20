# from CrawlStarbucks.services.data_service import get_all_drinks_from_db
from flask import request
from CrawlStarbucks.db.database import SessionLocal
from CrawlStarbucks.models import Drink, DrinkInfo, Category, Size
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased

def get_all_drinks():
    session = SessionLocal()
    type_id = request.args.get("type")
    key_search = request.args.get("search")
    min_calories = request.args.get("minCalories")
    max_calories = request.args.get("maxCalories")
    min_sugar = request.args.get("minSugar")
    max_sugar = request.args.get("maxSugar")
    min_caffeine = request.args.get("minCaffeine")
    max_caffeine = request.args.get("maxCaffeine")

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

    if key_search:
        query = query.filter(func.lower(Drink.name).like(f"%{key_search.lower()}%"))

    if min_calories:
        min_calories_int = int(min_calories)
        query = query.filter(InfoAlias.calories >= min_calories_int)

    if max_calories:
        max_calories_int = int(max_calories)
        query = query.filter(InfoAlias.calories <= max_calories_int)

    if min_sugar:
        min_sugar_int = int(min_sugar)
        query = query.filter(InfoAlias.sugars >= min_sugar_int)

    if max_sugar:
        max_sugar_int = int(max_sugar)
        query = query.filter(InfoAlias.sugars <= max_sugar_int)

    if min_caffeine:
        min_caffeine_int = int(min_caffeine)
        query = query.filter(InfoAlias.caffeine >= min_caffeine_int)

    if max_caffeine:
        max_caffeine_int = int(max_caffeine)
        query = query.filter(InfoAlias.caffeine <= max_caffeine_int)

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

def get_avg_drinks(drinks):
    session = SessionLocal()

    selected_categories = drinks

    # Aliases
    di = aliased(DrinkInfo)
    d = aliased(Drink)
    c = aliased(Category)

    # Subquery: lấy size nhỏ nhất cho mỗi drink
    min_size_subquery = (
        session.query(
            DrinkInfo.drink_id.label("drink_id"),
            func.min(DrinkInfo.size_id).label("min_size_id")
        )
        .group_by(DrinkInfo.drink_id)
        .subquery()
    )

    # Main query: join category -> drink -> drink_info (chỉ lấy size nhỏ nhất)
    query = (
        session.query(
            c.name.label("category_name"),
            func.avg(di.calories).label("avg_calories"),
            func.avg(di.sugars).label("avg_sugars"),
            func.avg(di.caffeine).label("avg_caffeine"),
            func.avg(di.total_fat).label("avg_total_fat")
        )
        .join(d, d.category_id == c.id)
        .join(di, di.drink_id == d.id)  # Join alias trước
        .join(min_size_subquery,
              (di.drink_id == min_size_subquery.c.drink_id) &
              (di.size_id == min_size_subquery.c.min_size_id))  # Sau đó mới join subquery
        .filter(c.name.in_(selected_categories))
        .group_by(c.name)
    )

    # Format kết quả
    DRINK_DATA = {
        row.category_name: {
            "calories": round(row.avg_calories or 0),
            "sugar": round(row.avg_sugars or 0),
            "caffeine": round(row.avg_caffeine or 0),
            "fat": round(row.avg_total_fat or 0),
        }
        for row in query.all()
    }

    return DRINK_DATA

