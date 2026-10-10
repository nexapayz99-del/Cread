import asyncio
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from config import API_ID, API_HASH
from database.mongo import accounts, channels
from services.vc_joiner import join_vc

_monitors = []

async def _on_channel_msg(client: Client, msg: Message, phone: str):
    """Fires when monitored channel posts/VC starts."""
    if msg.chat and msg.chat.id:
        await join_vc_by_phone(phone, msg.chat.id)

async def join_vc_by_phone(phone, chat_id):
    acc = await accounts.find_one({"phone": phone})
    if acc: await join_vc(acc, chat_id)

async def start_monitor(acc, channel_ids):
    """Start a listener userbot that auto-joins VC when channel goes live."""
    c = Client(f"mon_{acc['phone']}", api_id=API_ID, api_hash=API_HASH,
               session_string=acc["session"] if acc["type"] != "session_file" else None)
    await c.start()
    for cid in channel_ids:
        try:
            await c.join_chat(cid)
        except Exception:
            pass
        # Listen for all messages; when VC starts, handler joins
        c.add_handler(MessageHandler(
            lambda cl, m: asyncio.create_task(_on_channel_msg(cl, m, acc["phone"])),
            filters=None
        ))
    _monitors.append(c)
    asyncio.create_task(c.idle())

async def stop_monitors():
    for c in _monitors:
        try: await c.stop()
        except: pass
    _monitors.clear()
