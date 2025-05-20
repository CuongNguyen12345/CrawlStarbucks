from sqlalchemy.orm import sessionmaker
from CrawlStarbucks.db.database import engine, Base
from CrawlStarbucks.models import Category, Drink, DrinkInfo, Size

import requests
import pandas as pd



Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


def save_category_and_drinks(items, parent=None):
    for item in items:
        name = item.get("name")
        if not name:
            continue

        existing = session.query(Category).filter_by(name=name, parent_id=parent.id if parent else None).first()
        if existing:
            category = existing
        else:
            category = Category(name=name, parent_id=parent.id if parent else None)
            session.add(category)
            session.commit()

        products = item.get("products", [])
        for product in products:
            if not product.get("name"):
                continue

            # Bỏ qua sản phẩm có formCode là "Packaged"
            if product.get("formCode") == "Packaged":
                continue

            # existing_drink = session.query(Drink).filter_by(product_number=product.get("productNumber")).first()
            existing_drink = session.query(Drink).filter_by(
                product_number=product.get("productNumber"),
                form_code=product.get("formCode")
            ).first()

            if existing_drink:
                continue

            drink = Drink(
                name=product.get("name"),
                display_order=product.get("displayOrder"),
                form_code=product.get("formCode"),
                product_number=product.get("productNumber"),
                image_url=product.get("imageURL"),
                category_id=category.id
            )

            # Xử lý size
            size_list = []
            for size_data in product.get("sizes", []):
                size_code = size_data.get("sizeCode")
                if not size_code:
                    continue

                existing_size = session.query(Size).filter_by(size_code=size_code).first()
                if existing_size:
                    size = existing_size
                else:
                    size = Size(size_code=size_code)
                    session.add(size)
                    session.commit()

                size_list.append(size)

            drink.sizes = size_list

            session.add(drink)
            session.commit()

        children = item.get("children", [])
        if children:
            save_category_and_drinks(children, parent=category)


def fetch_and_save_detailed_info(drink: Drink):
    url = f"https://www.starbucks.com/apiproxy/v1/ordering/{drink.product_number}/{drink.form_code.lower()}"
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    excel_data = []  # Danh sách lưu dữ liệu sẽ ghi ra Excel

    try:
        res = requests.get(url, headers=headers)
        print(res.status_code)
        if res.status_code != 200:
            return

        response = res.json()
        products = response.get("products", [])

        if products and len(products) > 0:
            product = products[0]  # Lấy sản phẩm đầu tiên trong mảng
            sizes = product.get("sizes", [])  # Bây giờ lấy sizes từ sản phẩm
            print(sizes)
            for size in sizes:
                size_code = size.get("name")
                print(size_code)
                # Tìm hoặc tạo size
                size_obj = session.query(Size).filter_by(size_code=size_code).first()
                if not size_obj:
                    size_obj = Size(size_code=size_code)
                    session.add(size_obj)
                    session.commit()

                # Nếu đã có thì bỏ qua
                existing = session.query(DrinkInfo).filter_by(drink_id=drink.id, size_id=size_obj.id).first()
                if existing:
                    continue

                # Lấy nutrition data
                nutrition = size.get("nutrition", {})


                # Xử lý calories
                calories_data = nutrition.get("calories", {})
                calories = calories_data.get("displayValue") if isinstance(calories_data, dict) else calories_data
                calories_str = calories

                # Khởi tạo các giá trị dinh dưỡng
                total_fat = saturated_fat = trans_fat = cholesterol = sodium = None
                total_carbs = dietary_fiber = sugars = protein = caffeine = None

                # Xử lý các thông tin dinh dưỡng
                additional_facts = nutrition.get("additionalFacts", [])
                for fact in additional_facts:
                    fact_id = fact.get("id")

                    if fact_id == "totalFat":
                        total_fat = fact.get("value")
                        # Lấy subfacts cho saturated và trans fat
                        for subfact in fact.get("subfacts", []):
                            if subfact.get("id") == "saturatedFat":
                                saturated_fat = subfact.get("value")
                            elif subfact.get("id") == "transFat":
                                trans_fat = subfact.get("value")

                    elif fact_id == "cholesterol":
                        cholesterol = fact.get("value")

                    elif fact_id == "sodium":
                        sodium = fact.get("value")

                    elif fact_id == "totalCarbs":
                        total_carbs = fact.get("value")
                        # Lấy subfacts cho dietary fiber và sugars
                        for subfact in fact.get("subfacts", []):
                            if subfact.get("id") == "dietaryFiber":
                                dietary_fiber = subfact.get("value")
                            elif subfact.get("id") == "sugars":
                                sugars = subfact.get("value")

                    elif fact_id == "protein":
                        protein = fact.get("value")

                    elif fact_id == "caffeine":
                        caffeine = fact.get("value")

                # Xử lý thành phần
                ingredients_list = []
                for ingredient_item in size.get("ingredients", []):
                    if "name" in ingredient_item and ingredient_item["name"]:
                        ingredients_list.append(ingredient_item["name"])

                ingredients_str = ", ".join(ingredients_list)
                if len(ingredients_str) > 500:  # Giới hạn theo kích thước varchar(500)
                    ingredients_str = ingredients_str[:497] + "..."

                try:
                    # Tạo và lưu đối tượng DrinkInfo
                    info = DrinkInfo(
                        drink_id=drink.id,
                        size_id=size_obj.id,
                        ingredients=ingredients_str,
                        calories=calories_str,
                        total_fat=total_fat,
                        saturated_fat=saturated_fat,
                        trans_fat=trans_fat,
                        cholesterol=cholesterol,
                        sodium=sodium,
                        total_carbs=total_carbs,
                        dietary_fiber=dietary_fiber,
                        sugars=sugars,
                        protein=protein,
                        caffeine=caffeine
                    )
                    session.add(info)
                    session.commit()
                    print(f"Đã thêm thông tin cho {drink.name}, size {size_code}")
                except Exception as e:
                    session.rollback()
                    print(f"Lỗi khi lưu thông tin cho {drink.name}, size {size_code}: {e}")

                excel_data.append({
                    'Tên đồ uống': drink.name,
                    'Size': size_code,
                    'Calories': calories_str,
                    'Total Fat': total_fat,
                    'Saturated Fat': saturated_fat,
                    'Trans Fat': trans_fat,
                    'Cholesterol': cholesterol,
                    'Sodium': sodium,
                    'Total Carbs': total_carbs,
                    'Dietary Fiber': dietary_fiber,
                    'Sugars': sugars,
                    'Protein': protein,
                    'Caffeine': caffeine,
                    'Ingredients': ingredients_str
                })


        else:
            print("Không tìm thấy sản phẩm")

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu cho {drink.name}: {e}")

    if excel_data:
        try:
            df = pd.DataFrame(excel_data)
            df.to_excel("starbucks_nutrition.xlsx", index=False, engine='openpyxl')
            print("Đã lưu dữ liệu vào file starbucks_nutrition.xlsx")
        except Exception as e:
            print(f"Lỗi khi ghi file Excel: {e}")

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
        save_category_and_drinks(children)

        all_drinks = session.query(Drink).all()
        for drink in all_drinks:
            fetch_and_save_detailed_info(drink)
            # print(f"https://www.starbucks.com/apiproxy/v1/ordering/{drink.product_number}/{drink.form_code.lower()}")
    session.close()
