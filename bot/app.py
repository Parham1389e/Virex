from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from sqlalchemy import select
from config.settings import settings
from database.models import Product, User, Wallet
from database.session import SessionFactory

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with SessionFactory() as session:
        tg = update.effective_user; user = await session.scalar(select(User).where(User.telegram_id == tg.id))
        if user is None:
            user = User(telegram_id=tg.id, first_name=tg.first_name or "", username=tg.username); session.add(user); await session.flush(); session.add(Wallet(user_id=user.id)); await session.commit()
    keyboard = [[InlineKeyboardButton("💰 کیف پول", callback_data="balance"), InlineKeyboardButton("💳 شارژ", callback_data="card")], [InlineKeyboardButton("🛒 خرید", callback_data="products"), InlineKeyboardButton("🎫 پشتیبانی", callback_data="support")]]
    await update.message.reply_text("سلام! به Virex خوش آمدید 🌿", reply_markup=InlineKeyboardMarkup(keyboard))

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with SessionFactory() as s:
        user = await s.scalar(select(User).where(User.telegram_id == update.effective_user.id)); wallet = await s.scalar(select(Wallet).where(Wallet.user_id == user.id))
    await update.callback_query.answer(); await update.callback_query.message.reply_text(f"موجودی شما: {wallet.balance:,.2f} تومان")

async def card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(); await update.callback_query.message.reply_text(f"شماره کارت: {settings.card_number}\nبه نام: {settings.card_holder}\nرسید را پس از پرداخت ارسال کنید.")

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with SessionFactory() as s: rows = (await s.execute(select(Product).where(Product.available.is_(True)).limit(50))).scalars().all()
    text = "\n".join(f"#{p.id} {p.name} | {p.volume} | {p.duration} | {p.price:,.2f}" for p in rows) or "محصولی موجود نیست."
    await update.callback_query.answer(); await update.callback_query.message.reply_text(text)

def build_application():
    app = Application.builder().token(settings.bot_token).build(); app.add_handler(CommandHandler("start", start)); app.add_handler(CallbackQueryHandler(balance, pattern="^balance$")); app.add_handler(CallbackQueryHandler(card, pattern="^card$")); app.add_handler(CallbackQueryHandler(products, pattern="^products$")); return app
