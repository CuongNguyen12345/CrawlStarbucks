from sqlalchemy.orm import sessionmaker
from Starbucks.db.database import engine, Base
from models.Category import Category
from models.Drink import Drink
from models.Size import Size
import requests
import json

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_category_tree(items, parent=None):
    for item in items:
        name = item.get("name")
        if not name:
            continue

        # Tránh trùng lặp
        existing = session.query(Category).filter_by(name=name, parent_id=parent.id if parent else None).first()
        if existing:
            category = existing
        else:
            category = Category(name=name, parent_id=parent.id if parent else None)
            session.add(category)
            session.commit()

        # Đệ quy nếu có children
        children = item.get("children", [])
        if children:
            save_category_tree(children, parent=category)

def save_drinks(items, parent=None):
    for item in items:
        name = item.get("name")
        if not name:
            continue

        # Tìm lại category tương ứng
        category = session.query(Category).filter_by(name=name, parent_id=parent.id if parent else None).first()
        if not category:
            continue

        # Thêm sản phẩm (drinks) nếu có
        for product in item.get("products", []):
            # Tránh thêm trùng
            existing = session.query(Drink).filter_by(product_number=product.get("productNumber")).first()
            if existing:
                continue

            drink = Drink(
                name=product.get("name"),
                display_order=product.get("displayOrder"),
                product_number=product.get("productNumber"),
                image_url=product.get("imageURL"),
                category_id=category.id
            )
            session.add(drink)
            session.commit()

            
        # Đệ quy nếu có children
        children = item.get("children", [])
        if children:
            save_drinks(children, parent=category)

if __name__ == '__main__':
    url = 'https://www.starbucks.com/apiproxy/v1/ordering/menu'
    headers = {
        "User-Agent": "Mozilla/5.0",  # để tránh bị chặn
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    menus = data.get("menus", [])
    drinks_menu = next((menu for menu in menus if menu.get("id") == "drinks"), None)

    if drinks_menu:
        children = drinks_menu.get("children", [])
        save_category_tree(children)
        save_drinks(children)
    session.close()
