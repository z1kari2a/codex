import json
import os
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ForceReply)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

ASK_NAME, ASK_PHONE = range(2)

ORDERS_FILE = os.path.join(os.path.dirname(__file__), 'orders.json')

if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
        ORDERS = json.load(f)
else:
    ORDERS = []

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
    if not product:
        await update.callback_query.answer('حدث خطأ')
        return ConversationHandler.END
    context.user_data['order_product'] = product
    await update.callback_query.message.reply_text('ما اسمك؟', reply_markup=ForceReply(selective=True))
    return ASK_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_name'] = update.message.text
    await update.message.reply_text('رقم جوالك؟', reply_markup=ForceReply(selective=True))
    return ASK_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    product = context.user_data.get('order_product')
    name = context.user_data.get('order_name')
    ORDERS.append({'product_id': product['id'], 'name': name, 'phone': phone})
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ORDERS, f, ensure_ascii=False, indent=2)
    await update.message.reply_text('تم استلام طلبك!')
    return ConversationHandler.END

application = ApplicationBuilder().token(TOKEN or 'YOUR_TOKEN').build()
application.add_handler(CommandHandler('start', start))
application.add_handler(CallbackQueryHandler(show_categories, pattern='^categories$'))
application.add_handler(CallbackQueryHandler(show_products, pattern='^cat:'))
application.add_handler(CallbackQueryHandler(show_product_detail, pattern='^prod:'))

order_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_order, pattern='^order:')],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
    },
    fallbacks=[],
)

application.add_handler(order_conv)

if __name__ == '__main__':
    application.run_polling()
