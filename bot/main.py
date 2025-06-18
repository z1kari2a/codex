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
ADMIN_ID = os.environ.get("ADMIN_ID")

if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        ADMIN_ID = None

ASK_NAME, ASK_PHONE = range(2)
ADD_CATEGORY, ADD_NAME, ADD_PRICE, ADD_DESC = range(2, 6)

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

async def show_user_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_orders = [o for o in ORDERS if o.get('user_id') == user_id]
    if user_orders:
        lines = [f"{o['product_id']} - {o['name']} ({o['phone']})" for o in user_orders]
        text = '\n'.join(lines)
    else:
        text = 'لا توجد طلبات مسجلة.'
    await update.callback_query.edit_message_text(text)

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

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID is None or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text('غير مصرح لك بالدخول.')
        return
    keyboard = [
        [InlineKeyboardButton('🧾 مشاهدة الطلبات', callback_data='admin_orders')],
        [InlineKeyboardButton('➕ إضافة منتج', callback_data='admin_add')],
    ]
    await update.message.reply_text('لوحة التحكم', reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID is None or update.effective_user.id != ADMIN_ID:
        await update.callback_query.answer('غير مصرح')
        return
    if ORDERS:
        lines = [f"{o['product_id']} - {o['name']} ({o['phone']})" for o in ORDERS]
        text = '\n'.join(lines)
    else:
        text = 'لا توجد طلبات.'
    await update.callback_query.edit_message_text(text)

async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID is None or update.effective_user.id != ADMIN_ID:
        await update.callback_query.answer('غير مصرح')
        return ConversationHandler.END
    keyboard = [
        [InlineKeyboardButton(cat['name'], callback_data=f"addcat:{cat['id']}")]
        for cat in DATA['categories']
    ]
    await update.callback_query.edit_message_text('اختر تصنيف المنتج:', reply_markup=InlineKeyboardMarkup(keyboard))
    return ADD_CATEGORY

async def admin_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = update.callback_query.data.split(':')[1]
    context.user_data['new_prod_cat'] = cat_id
    await update.callback_query.message.reply_text('اسم المنتج؟', reply_markup=ForceReply(selective=True))
    return ADD_NAME

async def admin_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_prod_name'] = update.message.text
    await update.message.reply_text('السعر؟', reply_markup=ForceReply(selective=True))
    return ADD_PRICE

async def admin_add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_prod_price'] = update.message.text
    await update.message.reply_text('الوصف؟', reply_markup=ForceReply(selective=True))
    return ADD_DESC

async def admin_add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = context.user_data.get('new_prod_cat')
    name = context.user_data.get('new_prod_name')
    price = context.user_data.get('new_prod_price')
    desc = update.message.text

    product_id = f"{cat_id}_{len([p for p in DATA['products'] if p['category_id'] == cat_id]) + 1}"
    new_prod = {
        'id': product_id,
        'category_id': cat_id,
        'name': name,
        'price': price,
        'description': desc,
    }
    DATA['products'].append(new_prod)
    products_file = os.path.join(os.path.dirname(__file__), 'products.json')
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)
    await update.message.reply_text('تمت إضافة المنتج بنجاح')
    return ConversationHandler.END

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
    order = {
        'product_id': product['id'],
        'name': name,
        'phone': phone,
        'user_id': update.effective_user.id,
    }
    ORDERS.append(order)
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ORDERS, f, ensure_ascii=False, indent=2)
    await update.message.reply_text('تم استلام طلبك!')
    if ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"طلب جديد من {name} ({phone}) للمنتج {product['name']}"
        )
    return ConversationHandler.END

application = ApplicationBuilder().token(TOKEN or 'YOUR_TOKEN').build()
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('admin', admin_menu))
application.add_handler(CallbackQueryHandler(show_categories, pattern='^categories$'))
application.add_handler(CallbackQueryHandler(show_products, pattern='^cat:'))
application.add_handler(CallbackQueryHandler(show_product_detail, pattern='^prod:'))
application.add_handler(CallbackQueryHandler(show_user_orders, pattern='^orders$'))
application.add_handler(CallbackQueryHandler(admin_orders, pattern='^admin_orders$'))

order_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_order, pattern='^order:')],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
    },
    fallbacks=[],
)

application.add_handler(order_conv)

admin_add_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(admin_add_start, pattern='^admin_add$')],
    states={
        ADD_CATEGORY: [CallbackQueryHandler(admin_add_category, pattern='^addcat:')],
        ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_name)],
        ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_price)],
        ADD_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_desc)],
    },
    fallbacks=[],
)

application.add_handler(admin_add_conv)

if __name__ == '__main__':
    application.run_polling()
