import asyncio, base64, tempfile, os
from pyrogram import Client
from pyrogram.raw.functions.phone import JoinGroupCall, LeaveGroupCall
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from config import API_ID, API_HASH

_clients = {}  # phone -> Client

async def _get_client(acc):
    phone = acc["phone"]
    if phone in _clients:
        return _clients[phone]
    if acc["type"] == "session_file":
        data = base64.b64decode(acc["session"])
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".session")
        tmp.write(data); tmp.close()
        c = Client(tmp.name, api_id=API_ID, api_hash=API_HASH)
    else:
        c = Client(f"acc_{phone}", api_id=API_ID, api_hash=API_HASH,
                   session_string=acc["session"])
    await c.start()
    _clients[phone] = c
    return c

async def _get_call(client, chat_id):
    try:
        peer = await client.resolve_peer(chat_id)
    except Exception:
        return None, None
    try:
        if isinstance(peer, InputPeerChannel):
            full = await client.invoke(GetFullChannel(channel=peer))
        else:
            full = await client.invoke(GetFullChat(chat_id=peer.chat_id))
        call = full.full_chat.call
        if not call:
            return None, peer
        return call, peer
    except Exception:
        return None, None

async def join_vc(acc, chat_id):
    """Join one VC. Returns True if joined. Leaves after needed."""
    try:
        c = await _get_client(acc)
        call, peer = await _get_call(c, chat_id)
        if not call:
            return False
        params = await c.invoke(
            __import__("pyrogram.raw.functions.phone",
                       fromlist=["GetGroupCall"]).GetGroupCall(
                call=InputGroupCall(id=call.id, access_hash=call.access_hash),
                limit=1)
        )
        # JoinGroupCall requires params from GetGroupCall
        join = JoinGroupCall(
            call=InputGroupCall(id=call.id, access_hash=call.access_hash),
            join_as=peer,
            params=params.params,
            muted=True, video_stopped=True
        )
        await c.invoke(join)
        return True
    except Exception as e:
        print(f"[VC JOIN FAIL] {acc['phone']} -> {chat_id}: {e}")
        return False

async def leave_vc(acc, chat_id):
    try:
        c = await _get_client(acc)
        call, peer = await _get_call(c, chat_id)
        if not call: return False
        await c.invoke(LeaveGroupCall(
            call=InputGroupCall(id=call.id, access_hash=call.access_hash),
            source=0))
        return True
    except Exception:
        return False

async def join_all_channels_for_account(acc, channel_ids):
    """Join VC in up to 15 channels with the same account (like Musica)."""
    results = {}
    for cid in channel_ids:
        results[cid] = await join_vc(acc, cid)
        await asyncio.sleep(1.5)
    return results

async def stop_all():
    for c in _clients.values():
        try: await c.stop()
        except: pass
    _clients.clear()
