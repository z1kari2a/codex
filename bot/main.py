import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler, CommandHandler,
                          ContextTypes)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

with open(os.path.join(os.path.dirname(__file__), 'products.json'), 'r', encoding='utf-8') as f:
    DATA = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton('🛍️ المنتجات', callback_data='categories')],
        [InlineKeyboardButton('🧾 الطلبات', callback_data='orders')],
        [InlineKeyboardButton('📞 تواصل معنا', url='https://t.me/your_contact')],
        [InlineKeyboardButton('🌐 زيارة الموقع', url='https://example.com')],
    ]
    await update.message.reply_text('مرحبا بك في متجرنا الإلكتروني', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(cat['name'], callback_data=f"cat:{cat['id']}")]
                for cat in DATA['categories']]
    await update.callback_query.edit_message_text('اختر تصنيفاً:', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = update.callback_query.data.split(':')[1]
    products = [p for p in DATA['products'] if p['category_id'] == cat_id]
    keyboard = []
    for p in products:
        keyboard.append([InlineKeyboardButton(f"{p['name']} - {p['price']}", callback_data=f"prod:{p['id']}")])
    await update.callback_query.edit_message_text('المنتجات:', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prod_id = update.callback_query.data.split(':')[1]
    product = next((p for p in DATA['products'] if p['id'] == prod_id), None)
    if not product:
        await update.callback_query.answer('غير موجود')
        return
    keyboard = [[InlineKeyboardButton('🛒 اطلب الآن', callback_data=f"order:{prod_id}")]]
    text = f"{product['name']}\nالسعر: {product['price']}\n{product['description']}"
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prod_id = update.callback_query.data.split(':')[1]
    product = next((p for p in DATA['products'] if p['id'] == prod_id), None)
    if product:
        await update.callback_query.answer('تم استلام طلبك!')
    else:
        await update.callback_query.answer('حدث خطأ، حاول لاحقاً')

application = ApplicationBuilder().token(TOKEN or 'YOUR_TOKEN').build()
application.add_handler(CommandHandler('start', start))
application.add_handler(CallbackQueryHandler(show_categories, pattern='^categories$'))
application.add_handler(CallbackQueryHandler(show_products, pattern='^cat:'))
application.add_handler(CallbackQueryHandler(show_product_detail, pattern='^prod:'))
application.add_handler(CallbackQueryHandler(handle_order, pattern='^order:'))

if __name__ == '__main__':
    application.run_polling()
