from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.mongo import users, accounts, plans
from config import PLANS
from datetime import datetime, timedelta

ASK_NAME, ASK_PHONE, ASK_SESSION = range(3)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await users.update_one({"user_id": u.id},
        {"$setOnInsert": {"user_id": u.id, "username": u.username,
                          "joined_at": datetime.utcnow()}}, upsert=True)
    kb = [[InlineKeyboardButton("➕ Add Account", callback_data="addacc")],
          [InlineKeyboardButton("📊 My Plan", callback_data="myplan"),
           InlineKeyboardButton("📱 My Accounts", callback_data="myacc")],
          [InlineKeyboardButton("❤️ React", callback_data="react"),
           InlineKeyboardButton("👁 Views", callback_data="views")],
          [InlineKeyboardButton("🎙 Join VC", callback_data="joinevc")],
          [InlineKeyboardButton("🎲 Randomize Profile", callback_data="rand")]]
    await update.message.reply_text(
        "🎯 <b>VC Multi-Account Bot</b>\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

async def addacc_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.message.reply_text("Send <b>account name</b> (or /cancel):",
                               parse_mode="HTML")
    return ASK_NAME

async def addacc_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["acc_name"] = update.message.text.strip()
    await update.message.reply_text("Send <b>phone</b> (e.g. +919999999999):",
                                    parse_mode="HTML")
    return ASK_PHONE

async def addacc_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["acc_phone"] = update.message.text.strip()
    await update.message.reply_text(
        "Send one of:\n"
        "• Pyrogram session string\n"
        "• Telethon StringSession\n"
        "• HEX key\n"
        "• Upload <code>.session</code> file\n"
        "• Upload ZIP of sessions/JSONs\n",
        parse_mode="HTML")
    return ASK_SESSION

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled."); return ConversationHandler.END
