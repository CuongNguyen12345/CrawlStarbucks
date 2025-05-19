from flask import Flask, render_template, request
from CrawlStarbucks.controllers.drink_controller import get_all_drinks, get_all_categories, get_single_drink
app = Flask(__name__, static_folder='static', template_folder='templates')
@app.route('/')
def home():
    # drinks = get_all_drinks()
    # return render_template("index.html", drinks=drinks)
    drinks = get_all_drinks()  # list tất cả đồ uống
    categories = get_all_categories()
    page = request.args.get('page', 1, type=int)
    per_page = 6  # số phần tử mỗi trang

    start = (page - 1) * per_page
    end = start + per_page
    paginated_drinks = drinks[start:end]

    total_pages = (len(drinks) + per_page - 1) // per_page  # làm tròn lên

    return render_template('index.html',
                           drinks=paginated_drinks,
                           categories=categories,
                           page=page,
                           total_pages=total_pages,
                           total=len(drinks))


@app.route(f'/detail/<id>')
def detail(id):
    drink = get_single_drink(id)
    print(drink)
    return render_template('detail.html', drink=drink)

if __name__ == '__main__':
    app.run(debug=True)
