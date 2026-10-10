from telegram import Update
from telegram.ext import ContextTypes
from database.mongo import users, plans
from config import OWNER_ID, PLANS
from datetime import datetime, timedelta

def owner_only(func):
    async def w(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("⛔ Owner only.")
            return
        return await func(update, ctx)
    return w

@owner_only
async def grant(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/grant <user_id> <plan> <reactions> <views> <vc_joins> <accounts>"""
    try:
        uid, plan, r, v, vc, ac = ctx.args
        uid, r, v, vc, ac = map(int, (uid, r, v, vc, ac))
    except Exception:
        await update.message.reply_text(
            "Usage: /grant uid plan react views vc accounts"); return
    if plan not in PLANS:
        await update.message.reply_text("Bad plan."); return
    await plans.update_one({"user_id": uid},
        {"$set": {"plan": plan, "reactions": r, "views": v,
                  "vc_joins": vc, "accounts": ac,
                  "expires_at": datetime.utcnow()+timedelta(days=30)}},
        upsert=True)
    await update.message.reply_text(f"✅ Granted {plan} to {uid}.")

@owner_only
async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /broadcast <msg>"); return
    msg = " ".join(ctx.args)
    total = 0
    async for u in users.find({}):
        try:
            await ctx.bot.send_message(u["user_id"], msg); total += 1
        except Exception: pass
    await update.message.reply_text(f"📢 Sent to {total} users.")
