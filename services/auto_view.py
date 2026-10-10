import asyncio
from pyrogram import Client
from pyrogram.raw.functions.messages import GetMessagesViews
from config import API_ID, API_HASH

async def view_post(acc, chat_id, msg_id):
    c = Client(f"v_{acc['phone']}", api_id=API_ID, api_hash=API_HASH,
               session_string=acc["session"])
    await c.start()
    try:
        peer = await c.resolve_peer(chat_id)
        await c.invoke(GetMessagesViews(
            peer=peer, id=[msg_id], increment=True))
        return True
    except Exception as e:
        print("view fail:", e); return False
    finally:
        await c.stop()

async def auto_view_all(accounts_list, chat_id, msg_id):
    return await asyncio.gather(*[view_post(a, chat_id, msg_id) for a in accounts_list])
