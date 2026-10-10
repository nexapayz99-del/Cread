import io
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.account_manager import (
    import_session_string, import_hex_key, import_session_file,
    import_zip, list_accounts, remove_account
)
from database.mongo import plans, accounts as acc_col
from config import PLANS

END = ConversationHandler.END

async def handle_session_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    name  = ctx.user_data.get("acc_name", "Unknown")
    phone = ctx.user_data.get("acc_phone", "")

    plan  = await plans.find_one({"user_id": u.id}) or {"plan": "free"}
    limit = PLANS[plan["plan"]]["accounts"]
    count = await acc_col.count_documents({"owner_id": u.id})

    if count >= limit:
        await update.message.reply_text(
            f"❌ Plan limit reached ({limit} accounts).\n"
            f"Contact owner to upgrade."
        )
        return END

    # Document upload (.session / .zip)
    doc = update.message.document
    if doc:
        try:
            data = await doc.download_as_bytearray()
        except Exception as e:
            await update.message.reply_text(f"❌ Download failed: {e}")
            return END

        fname = (doc.file_name or "").lower()
        try:
            if fname.endswith(".zip"):
                n = await import_zip(u.id, bytes(data), name)
                await update.message.reply_text(f"✅ Imported {n} account(s) from ZIP.")
            elif fname.endswith(".session"):
                await import_session_file(u.id, bytes(data), doc.file_name, name, phone)
                await update.message.reply_text("✅ .session file imported.")
            else:
                await update.message.reply_text("❌ Only .session or .zip allowed.")
        except Exception as e:
            await update.message.reply_text(f"❌ Import failed: {e}")
        return END

    # Text paste
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("❌ Empty input. Try again.")
        return END

    try:
        if len(text) > 250 and text.count(":") >= 3:
            # Pyrogram-style session (long base64)
            await import_session_string(u.id, text, name, phone, "pyrogram")
            await update.message.reply_text("✅ Pyrogram session imported.")
        elif text.startswith("1") and len(text) > 150:
            # Telethon StringSession
            await import_session_string(u.id, text, name, phone, "telethon")
            await update.message.reply_text("✅ Telethon session imported.")
        else:
            # Hex key or short string
            await import_hex_key(u.id, text, name, phone)
            await update.message.reply_text("✅ Session/HEX imported.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to import: {e}")

    return END


async def my_accounts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    rows = await list_accounts(q.from_user.id)
    if not rows:
        await q.message.reply_text("📭 No accounts yet. Use ➕ Add Account.")
        return
    lines = []
    for r in rows:
        health = (r.get("health") or {}).get("status", "unknown")
        lines.append(f"• <code>{r.get('phone','?')}</code> — {r.get('name','?')} [{health}]")
    await q.message.reply_text(
        "<b>Your Accounts</b>\n" + "\n".join(lines),
        parse_mode="HTML"
    )


async def remove_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /remove <phone>")
        return
    ok = await remove_account(update.effective_user.id, ctx.args[0])
    await update.message.reply_text("🗑 Removed." if ok else "❌ Not found.")