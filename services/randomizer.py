import io, zipfile, random, asyncio
from pyrogram import Client
from PIL import Image
from config import API_ID, API_HASH
from utils.indian_names import random_indian_name

async def change_profile(acc, name=None, photo_bytes=None):
    c = Client(f"p_{acc['phone']}", api_id=API_ID, api_hash=API_HASH,
               session_string=acc["session"])
    await c.start()
    try:
        new_name = name or random_indian_name()
        await c.update_profile(first_name=new_name)
        if photo_bytes:
            f = io.BytesIO(photo_bytes); f.name = "dp.jpg"
            await c.set_profile_photo(photo=f)
        return new_name
    finally:
        await c.stop()

async def randomize_all(accounts_list, zip_bytes=None):
    """zip_bytes: ZIP of dp images. Each account gets a random one."""
    photos = []
    if zip_bytes:
        z = zipfile.ZipFile(io.BytesIO(zip_bytes))
        for n in z.namelist():
            if n.lower().endswith((".jpg",".jpeg",".png")):
                photos.append(z.read(n))
    results = {}
    for a in accounts_list:
        photo = random.choice(photos) if photos else None
        try:
            nm = await change_profile(a, photo_bytes=photo)
            results[a["phone"]] = nm
        except Exception as e:
            results[a["phone"]] = f"fail: {e}"
        await asyncio.sleep(2)
    return results
