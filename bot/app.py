from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters
from sqlalchemy import select
from config.settings import settings
from database.models import Config, Order, Product, TopUp, User, Wallet
from database.session import SessionFactory
from services.admin import AdminService
from services.orders import OrderService
from services.topups import TopUpService

AMOUNT, RECEIPT, REJECT_REASON = range(3)
def is_admin(update): return update.effective_user and update.effective_user.id in settings.admin_ids
async def get_user(session, tg):
    user=await session.scalar(select(User).where(User.telegram_id==tg.id))
    if user is None:
        user=User(telegram_id=tg.id, first_name=tg.first_name or "", username=tg.username); session.add(user); await session.flush(); session.add(Wallet(user_id=user.id)); await session.flush()
    return user
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    async with SessionFactory() as s: await get_user(s,update.effective_user); await s.commit()
    await update.message.reply_text("سلام! به Virex خوش آمدید 🌿",reply_markup=main_keyboard())
def main_keyboard(): return InlineKeyboardMarkup([[InlineKeyboardButton("💰 کیف پول",callback_data="balance"),InlineKeyboardButton("💳 شارژ",callback_data="card")],[InlineKeyboardButton("🛒 محصولات",callback_data="products"),InlineKeyboardButton("📦 سفارش‌های من",callback_data="orders")],[InlineKeyboardButton("🎫 پشتیبانی",callback_data="support")]])
async def balance(update,context):
    async with SessionFactory() as s:
        user=await s.scalar(select(User).where(User.telegram_id==update.effective_user.id)); wallet=await s.scalar(select(Wallet).where(Wallet.user_id==user.id))
    await update.callback_query.answer(); await update.callback_query.message.reply_text(f"موجودی: {wallet.balance:,.2f}")
async def card(update,context):
    await update.callback_query.answer(); await update.callback_query.message.reply_text(f"کارت: {settings.card_number}\nبه نام: {settings.card_owner}\nابتدا مبلغ را ارسال کنید:")
    return AMOUNT
async def amount_received(update,context):
    try: context.user_data["topup_amount"]=Decimal(update.message.text.strip())
    except Exception: await update.message.reply_text("مبلغ نامعتبر است."); return AMOUNT
    await update.message.reply_text("اکنون رسید را به صورت عکس یا فایل PDF ارسال کنید."); return RECEIPT
async def receipt_received(update,context):
    message=update.message; doc=message.document; photo=message.photo[-1] if message.photo else None
    if not doc and not photo: await message.reply_text("لطفاً عکس یا PDF رسید را ارسال کنید."); return RECEIPT
    file_id=doc.file_id if doc else photo.file_id; mime=(doc.mime_type if doc else "image/jpeg")
    async with SessionFactory() as s:
        try:
            tgfile=await context.bot.get_file(file_id); payload=await tgfile.download_as_bytearray()
            if len(payload)>settings.receipt_max_bytes: raise ValueError("فایل بزرگ است")
            user=await get_user(s,update.effective_user); item=await TopUpService(s).create(user.id,context.user_data["topup_amount"],file_id,mime,len(payload)); await s.commit()
            await message.reply_text(f"درخواست شارژ #{item.id} ثبت شد و برای بررسی ارسال می‌شود.")
            for admin in settings.admin_ids:
                await context.bot.send_message(admin,f"شارژ جدید #{item.id}\nکاربر: {user.telegram_id}\nمبلغ: {item.amount}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأیید",callback_data=f"topup:approve:{item.id}"),InlineKeyboardButton("❌ رد",callback_data=f"topup:reject:{item.id}")]]))
                await context.bot.send_document(admin,document=file_id,caption=f"رسید درخواست #{item.id}") if doc else await context.bot.send_photo(admin,photo=file_id,caption=f"رسید درخواست #{item.id}")
        except Exception as exc: await s.rollback(); await message.reply_text(f"رسید پذیرفته نشد: {exc}"); return RECEIPT
    context.user_data.clear(); return ConversationHandler.END
async def admin_callback(update,context):
    q=update.callback_query; await q.answer()
    if not is_admin(update): return
    _,action,raw=q.data.split(":"); tid=int(raw)
    async with SessionFactory() as s:
        if action=="approve": await AdminService(s).approve_topup(tid); await s.commit(); await q.edit_message_reply_markup(None); await q.message.reply_text("تأیید شد.")
        else: context.user_data["reject_topup"]=tid; await q.message.reply_text("دلیل رد را ارسال کنید."); return REJECT_REASON
async def reject_reason(update,context):
    if not is_admin(update): return ConversationHandler.END
    tid=context.user_data.pop("reject_topup",None)
    async with SessionFactory() as s: await AdminService(s).reject_topup(tid,update.message.text); await s.commit()
    await update.message.reply_text("درخواست رد شد."); return ConversationHandler.END
async def products(update,context):
    async with SessionFactory() as s: rows=(await s.execute(select(Product).where(Product.available.is_(True)).limit(50))).scalars().all()
    keys=[[InlineKeyboardButton(f"{p.name} | {p.price:,.0f}",callback_data=f"buy:{p.id}")] for p in rows]
    await update.callback_query.answer(); await update.callback_query.message.reply_text("محصول را انتخاب کنید:",reply_markup=InlineKeyboardMarkup(keys or [[InlineKeyboardButton("موجود نیست",callback_data="noop")]]))
async def buy(update,context):
    pid=int(update.callback_query.data.split(":")[1]); await update.callback_query.answer(); await update.callback_query.message.reply_text("خرید با موجودی کیف پول انجام شود؟",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأیید خرید",callback_data=f"pay:{pid}")]]))
async def pay(update,context):
    pid=int(update.callback_query.data.split(":")[1]); key=f"telegram:{update.effective_user.id}:{update.callback_query.id}"
    async with SessionFactory() as s:
        try:
            user=await s.scalar(select(User).where(User.telegram_id==update.effective_user.id)); order=await OrderService(s).purchase(user.id,pid,key); await s.commit(); config=await s.scalar(select(Config).where(Config.id==order.config_id)); await update.callback_query.message.reply_text("پرداخت موفق بود. کانفیگ ارسال می‌شود."); await update.callback_query.message.reply_text(config.value); await OrderService(s).mark_delivered(order.id); await s.commit()
        except Exception as exc: await s.rollback(); await update.callback_query.message.reply_text(f"خرید انجام نشد: {exc}")
async def orders(update,context):
    async with SessionFactory() as s:
        user=await s.scalar(select(User).where(User.telegram_id==update.effective_user.id)); rows=(await s.execute(select(Order).where(Order.user_id==user.id).order_by(Order.id.desc()).limit(20))).scalars().all()
    text="\n".join(f"#{o.id} | {o.status} | تحویل: {o.delivery_status}" for o in rows) or "سفارشی ندارید."
    await update.callback_query.answer(); await update.callback_query.message.reply_text(text)
def build_application():
    app=Application.builder().token(settings.bot_token).build(); receipt=ConversationHandler(entry_points=[CallbackQueryHandler(card,pattern="^card$")],states={AMOUNT:[MessageHandler(filters.TEXT & ~filters.COMMAND,amount_received)],RECEIPT:[MessageHandler(filters.PHOTO|filters.Document.ALL,receipt_received)]},fallbacks=[]); reject=ConversationHandler(entry_points=[CallbackQueryHandler(admin_callback,pattern=r"^topup:reject:\d+$")],states={REJECT_REASON:[MessageHandler(filters.TEXT & ~filters.COMMAND,reject_reason)]},fallbacks=[]); app.add_handler(CommandHandler("start",start)); app.add_handler(receipt); app.add_handler(reject); app.add_handler(CallbackQueryHandler(admin_callback,pattern=r"^topup:approve:\d+$")); app.add_handler(CallbackQueryHandler(balance,pattern="^balance$")); app.add_handler(CallbackQueryHandler(products,pattern="^products$")); app.add_handler(CallbackQueryHandler(buy,pattern=r"^buy:\d+$")); app.add_handler(CallbackQueryHandler(pay,pattern=r"^pay:\d+$")); app.add_handler(CallbackQueryHandler(orders,pattern="^orders$")); return app
