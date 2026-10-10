import io
from telegram import Update
from telegram.ext import ContextTypes
from services.account_manager import (
    import_session_string, import_hex_key, import_session_file,
    import_zip, list_accounts, remove_account
)
from database.mongo import plans, accounts as acc_col
from config import PLANS

async def handle_session_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Called after ASK_SESSION."""
    u = update.effective_user
    name = ctx.user_data["acc_name"]; phone = ctx.user_data["acc_phone"]
    plan = await plans.find_one({"user_id": u.id}) or {"plan":"free"}
    limit = PLANS[plan["plan"]]["accounts"]
    count = await acc_col.count_documents({"owner_id": u.id})
    if count >= limit:
        await update.message.reply_text(f"❌ Plan limit reached ({limit}).")
        return

    doc = update.message.document
    if doc:
        data = await doc.download_as_bytearray()
        if doc.file_name.endswith(".zip"):
            n = await import_zip(u.id, bytes(data), name)
            await update.message.reply_text(f"✅ Imported {n} accounts from ZIP.")
        elif doc.file_name.endswith(".session"):
            await import_session_file(u.id, bytes(data), doc.file_name, name, phone)
            await update.message.reply_text("✅ .session imported.")
        return

    text = (update.message.text or "").strip()
    if len(text) > 300 and text.count(":") >= 3:
        await import_session_string(u.id, text, name, phone, "pyrogram")
        await update.message.reply_text("✅ Pyrogram session imported.")
    elif text.startswith("1") and len(text) > 200:  # Telethon
        await import_session_string(u.id, text, name, phone, "telethon")
        await update.message.reply_text("✅ Telethon session imported.")
    else:
        await import_hex_key(u.id, text, name, phone)
        await update.message.reply_text("✅ HEX key imported.")

async def my_accounts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    rows = await list_accounts(q.from_user.id)
    if not rows:
        await q.message.reply_text("No accounts. Use ➕ Add Account."); return
    text = "\n".join(
        f"• <code>{r['phone']}</code> — {r['name']} [{r.get('health',{}).get('status','?')}]"
        for r in rows)
    await q.message.reply_text(text, parse_mode="HTML")

async def remove_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /remove <phone>"); return
    ok = await remove_account(update.effective_user.id, ctx.args[0])
    await update.message.reply_text("🗑 Removed." if ok else "Not found.")
