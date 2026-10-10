from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.mongo import plans
from config import PLANS

async def my_plan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    p = await plans.find_one({"user_id": q.from_user.id}) or {"plan":"free"}
    lim = PLANS[p["plan"]]
    await q.message.reply_text(
        f"<b>Plan:</b> {p['plan']}\n"
        f"Reactions: {p.get('reactions', lim['reactions'])}\n"
        f"Views: {p.get('views', lim['views'])}\n"
        f"VC Joins: {p.get('vc_joins', lim['vc_joins'])}\n"
        f"Accounts: {p.get('accounts', lim['accounts'])}",
        parse_mode="HTML")
