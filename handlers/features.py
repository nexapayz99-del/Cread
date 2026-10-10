import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database.mongo import accounts as acc_col, plans
from config import PLANS
from services.auto_react import auto_react_all
from services.auto_view import auto_view_all
from services.vc_joiner import join_all_channels_for_account
from services.randomizer import randomize_all

async def _user_accounts(uid):
    cur = acc_col.find({"owner_id": uid, "active": True})
    return await cur.to_list(length=1000)

async def _check_plan(uid, key, needed):
    p = await plans.find_one({"user_id": uid}) or {"plan": "free"}
    limit = PLANS[p["plan"]][key]
    used = p.get(key, limit)
    if needed > used:
        return False, f"❌ Plan limit: {used} (requested {needed})"
    return True, None

async def react_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /react <channel_id> <msg_id> [emoji]")
        return
    try:
        chat_id = int(ctx.args[0]); msg_id = int(ctx.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid channel_id or msg_id.")
        return
    emoji = ctx.args[2] if len(ctx.args) > 2 else None

    accs = await _user_accounts(uid)
    if not accs:
        await update.message.reply_text("❌ No active accounts.")
        return
    ok, err = await _check_plan(uid, "reactions", len(accs))
    if not ok:
        await update.message.reply_text(err); return

    await update.message.reply_text(f"⏳ Sending {len(accs)} reactions...")
    results = await auto_react_all(accs, chat_id, msg_id, emoji)
    sent = sum(1 for r in results if r)
    await update.message.reply_text(f"✅ Reactions sent: {sent}/{len(accs)}")

async def views_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /views <channel_id> <msg_id>")
        return
    try:
        chat_id = int(ctx.args[0]); msg_id = int(ctx.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid input.")
        return

    accs = await _user_accounts(uid)
    if not accs:
        await update.message.reply_text("❌ No active accounts.")
        return
    ok, err = await _check_plan(uid, "views", len(accs))
    if not ok:
        await update.message.reply_text(err); return

    await update.message.reply_text(f"⏳ Sending {len(accs)} views...")
    results = await auto_view_all(accs, chat_id, msg_id)
    sent = sum(1 for r in results if r)
    await update.message.reply_text(f"✅ Views sent: {sent}/{len(accs)}")

async def joinvc_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not ctx.args:
        await update.message.reply_text("Usage: /joinvc <channel1> [channel2] ...")
        return
    try:
        channels = [int(x) for x in ctx.args]
    except ValueError:
        await update.message.reply_text("❌ All must be numeric chat IDs.")
        return

    accs = await _user_accounts(uid)
    if not accs:
        await update.message.reply_text("❌ No active accounts.")
        return

    ok, err = await _check_plan(uid, "vc_joins", len(channels))
    if not ok:
        await update.message.reply_text(err); return

    await update.message.reply_text(
        f"⏳ Joining {len(channels)} VC(s) with {len(accs)} account(s)...")

    total_joined = 0
    for acc in accs:
        try:
            res = await join_all_channels_for_account(acc, channels)
            total_joined += sum(1 for v in res.values() if v)
        except Exception as e:
            print(f"joinvc err {acc.get('phone')}: {e}")

    await update.message.reply_text(
        f"✅ VC joins attempted: {total_joined}")

async def randomize_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    accs = await _user_accounts(uid)
    if not accs:
        await update.message.reply_text("❌ No active accounts.")
        return

    zip_bytes = None
    if update.message.document and update.message.document.file_name.endswith(".zip"):
        zip_bytes = bytes(await update.message.document.download_as_bytearray())

    await update.message.reply_text(f"⏳ Randomizing {len(accs)} accounts...")
    results = await randomize_all(accs, zip_bytes)
    preview = "\n".join(f"• {k} → {v}" for k, v in list(results.items())[:10])
    await update.message.reply_text(
        f"✅ Done.\n<pre>{preview}</pre>", parse_mode="HTML")
