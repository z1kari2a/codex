import os
import json
from flask import Flask, render_template_string

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'bot', 'products.json')
ORDERS_FILE = os.path.join(BASE_DIR, 'bot', 'orders.json')

with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
    DATA = json.load(f)

if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
        ORDERS = json.load(f)
else:
    ORDERS = []

app = Flask(__name__)
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'your_bot')

def product_link(product_id):
    return f"https://t.me/{BOT_USERNAME}?start={product_id}"

@app.route('/')
def index():
    html = ['<h1>المنتجات</h1>']
    for cat in DATA['categories']:
        html.append(f"<h2>{cat['name']}</h2><ul>")
        for p in [p for p in DATA['products'] if p['category_id'] == cat['id']]:
            html.append(
                f"<li><b>{p['name']}</b> - {p['price']} - {p['description']} "
                f"<a href='{product_link(p['id'])}'>اطلب عبر البوت</a></li>")
        html.append('</ul>')
    return render_template_string('\n'.join(html))

@app.route('/orders')
def show_orders():
    html = ['<h1>الطلبات</h1><ul>']
    for o in ORDERS:
        html.append(
            f"<li>{o['name']} ({o['phone']}) - منتج: {o['product_id']}</li>")
    html.append('</ul>')
    return render_template_string('\n'.join(html))

if __name__ == '__main__':
    app.run(debug=True)
