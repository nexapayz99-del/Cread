import asyncio, random
from pyrogram import Client
from pyrogram.raw.functions.messages import SendReaction
from pyrogram.raw.types import ReactionEmoji
from config import API_ID, API_HASH

EMOJIS = ["👍","🔥","❤️","🎉","😁","👏","💯","⚡"]

async def react_to_post(acc, chat_id, msg_id, emoji=None):
    c = Client(f"r_{acc['phone']}", api_id=API_ID, api_hash=API_HASH,
               session_string=acc["session"])
    await c.start()
    try:
        peer = await c.resolve_peer(chat_id)
        await c.invoke(SendReaction(
            peer=peer,
            msg_id=msg_id,
            reaction=[ReactionEmoji(emoticon=emoji or random.choice(EMOJIS))]
        ))
        return True
    except Exception as e:
        print("react fail:", e)
        return False
    finally:
        await c.stop()

async def auto_react_all(accounts_list, chat_id, msg_id, emoji=None):
    tasks = [react_to_post(a, chat_id, msg_id, emoji) for a in accounts_list]
    return await asyncio.gather(*tasks)
