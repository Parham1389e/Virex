from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from config.settings import settings
from database.models import User, Wallet
from database.session import SessionFactory
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with SessionFactory() as session:
        tg=update.effective_user; user=await session.scalar(select(User).where(User.telegram_id==tg.id))
        if not user: user=User(telegram_id=tg.id, first_name=tg.first_name or "", username=tg.username); session.add(user); await session.flush(); session.add(Wallet(user_id=user.id)); await session.commit()
    await update.message.reply_text("سلام! به Virex خوش آمدید 🌿", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 کیف پول", callback_data="balance")],[InlineKeyboardButton("💳 اطلاعات کارت", callback_data="card")],[InlineKeyboardButton("🛒 محصولات", callback_data="products")],[InlineKeyboardButton("🎫 پشتیبانی", callback_data="support")]]))
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with SessionFactory() as s: user=await s.scalar(select(User).where(User.telegram_id==update.effective_user.id)); wallet=await s.scalar(select(Wallet).where(Wallet.user_id==user.id))
    await update.callback_query.answer(); await update.callback_query.message.reply_text(f"موجودی شما: {wallet.balance:,.2f} تومان")
async def card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(); await update.callback_query.message.reply_text(f"شماره کارت: {settings.card_number}\nبه نام: {settings.card_holder}\nپس از پرداخت، رسید و مبلغ را ارسال کنید.")
def build_application():
    from telegram.ext import Application, CallbackQueryHandler, CommandHandler
    app=Application.builder().token(settings.bot_token).build(); app.add_handler(CommandHandler("start", start)); app.add_handler(CallbackQueryHandler(balance, pattern="^balance$")); app.add_handler(CallbackQueryHandler(card, pattern="^card$")); return app
