import os, io, json, zipfile, tempfile, asyncio
from datetime import datetime
from pyrogram import Client as PyroClient
from telethon import TelegramClient
from telethon.sessions import StringSession
from database.mongo import accounts
from config import API_ID, API_HASH

async def import_session_string(owner_id, session_str, name, phone, kind="pyrogram"):
    """kind: pyrogram | telethon"""
    doc = {
        "owner_id": owner_id, "name": name, "phone": phone,
        "session": session_str, "type": kind, "active": True,
        "health": {"status": "unknown", "checked_at": None},
        "joined_vcs": [], "created_at": datetime.utcnow()
    }
    await accounts.update_one(
        {"owner_id": owner_id, "phone": phone},
        {"$set": doc}, upsert=True
    )
    return True

async def import_hex_key(owner_id, hex_data, name, phone):
    """hex_data = session string encoded as hex, or 2FA hex token."""
    try:
        session_str = bytes.fromhex(hex_data).decode()
    except Exception:
        session_str = hex_data  # fallback treat as raw
    return await import_session_string(owner_id, session_str, name, phone, "hex")

async def import_session_file(owner_id, file_bytes, filename, name, phone):
    """Uploaded .session file (sqlite). Convert to string session."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".session")
    tmp.write(file_bytes); tmp.close()
    # Pyrogram can't directly convert; store path-based session in Mongo as base64
    import base64
    b64 = base64.b64encode(file_bytes).decode()
    doc = {
        "owner_id": owner_id, "name": name, "phone": phone,
        "session": b64, "type": "session_file", "active": True,
        "health": {"status": "unknown", "checked_at": None},
        "joined_vcs": [], "created_at": datetime.utcnow()
    }
    await accounts.update_one(
        {"owner_id": owner_id, "phone": phone},
        {"$set": doc}, upsert=True
    )
    os.unlink(tmp.name)
    return True

async def import_zip(owner_id, zip_bytes, name_prefix):
    """ZIP with .session + .json (Telethon) files, one per account."""
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    imported = 0
    for info in z.infolist():
        if info.filename.endswith(".session"):
            data = z.read(info.filename)
            phone = info.filename.split("/")[-1].replace(".session","")
            await import_session_file(owner_id, data, info.filename,
                                      f"{name_prefix} {phone}", phone)
            imported += 1
        elif info.filename.endswith(".json"):
            meta = json.loads(z.read(info.filename))
            await import_session_string(
                owner_id,
                meta.get("session_string",""),
                meta.get("name", name_prefix),
                meta.get("phone",""),
                "telethon"
            )
            imported += 1
    return imported

async def list_accounts(owner_id):
    cur = accounts.find({"owner_id": owner_id})
    return await cur.to_list(length=1000)

async def remove_account(owner_id, phone):
    r = await accounts.delete_one({"owner_id": owner_id, "phone": phone})
    return r.deleted_count > 0
