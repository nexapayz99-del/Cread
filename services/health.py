import asyncio, re
from pyrogram import Client
from config import API_ID, API_HASH
from database.mongo import accounts
from datetime import datetime

SPAMBOT = "SpamBot"

async def check_account(acc):
    c = Client(f"h_{acc['phone']}", api_id=API_ID, api_hash=API_HASH,
               session_string=acc["session"])
    try:
        await c.start()
        await c.send_message(SPAMBOT, "/start")
        await asyncio.sleep(3)
        msgs = [m async for m in c.get_chat_history(SPAMBOT, limit=1)]
        if not msgs:
            status = "unknown"
        else:
            text = msgs[0].text or ""
            if "Good news" in text or "no limits" in text.lower():
                status = "ok"
            elif "limited" in text.lower() or "spam" in text.lower():
                status = "banned"
            else:
                status = "unknown"
        await accounts.update_one(
            {"_id": acc["_id"]},
            {"$set": {"health.status": status,
                      "health.checked_at": datetime.utcnow()}})
        return status
    except Exception as e:
        print("health fail:", e); return "error"
    finally:
        try: await c.stop()
        except: pass
