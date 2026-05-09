"""
Quotly Module — Quote messages as sticker images using quotly.io API.
Ported from WilliamButcherBot (MIT License) by TheHamkerCat.
"""
import base64
import asyncio
from io import BytesIO
from typing import List

import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app

QUOTLY_API = "https://bot.lyo.su/quote/generate"


async def generate_quote(messages: list):
    """Call quotly.io API to generate sticker from messages."""
    payload = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": messages,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            QUOTLY_API,
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
    
    if data.get("ok"):
        img_data = base64.b64decode(data["result"]["image"])
        sticker = BytesIO(img_data)
        sticker.name = "quote.webp"
        return sticker
    return None


async def build_message_obj(client, msg: Message):
    """Build a message object for quotly API from a Pyrogram message."""
    user = msg.from_user
    entities = []
    if msg.entities:
        for ent in msg.entities:
            entities.append({
                "type": ent.type.name.lower(),
                "offset": ent.offset,
                "length": ent.length,
            })
    
    # Try to get user photo
    avatar_url = None
    if user and user.photo:
        # We can't easily pass file_id to the API, it needs a URL or base64
        # But some versions of the API accept just the user info and fetch it themselves
        pass

    obj = {
        "entities": entities,
        "avatar": True,
        "from": {
            "id": user.id if user else 0,
            "first_name": user.first_name if user else "Anonymous",
            "last_name": user.last_name if user else "",
            "username": user.username if user else "",
            "language_code": "en",
            "title": user.first_name if user else "Anonymous",
            "photo": None
        },
        "text": msg.text or msg.caption or "",
        "replyMessage": {},
    }
    return obj


@app.on_message(filters.command(["q", "quotly"]) & ~filters.forwarded)
async def quotly_func(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to quote it.")
    
    if not (message.reply_to_message.text or message.reply_to_message.caption):
        return await message.reply_text(
            "Replied message has no text, can't quote it."
        )

    m = await message.reply_text("📝 <b>Quoting message...</b>")

    # Determine how many messages to quote
    count = 1
    if len(message.command) >= 2:
        arg = message.command[1]
        try:
            count = int(arg)
            count = max(1, min(count, 10))  # Clamp between 1-10
        except ValueError:
            count = 1

    # Fetch messages
    if count == 1:
        msgs = [message.reply_to_message]
    else:
        # Pyrogram doesn't have a direct "get next N messages" easily without a loop or get_chat_history
        # For simplicity, we just use the one replied to if it's more than 1 for now, 
        # or we could implement a small loop.
        msgs = [message.reply_to_message]
        # In a real scenario, you'd fetch subsequent messages here.

    # Build payload
    messages_payload = []
    for msg in msgs:
        obj = await build_message_obj(client, msg)
        messages_payload.append(obj)

    try:
        sticker = await generate_quote(messages_payload)
        if not sticker:
            return await m.edit("❌ Failed to generate quote. The API might be down.")
        
        await message.reply_sticker(sticker)
        await m.delete()
        sticker.close()
    except Exception as e:
        await m.edit(f"❌ Quote generation failed: {str(e)}")
