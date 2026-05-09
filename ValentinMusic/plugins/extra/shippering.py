"""
Shippering Module — Pick a random "couple of the day" in group chats.
Ported from WilliamButcherBot (MIT License) by TheHamkerCat.
"""
import random
from datetime import datetime

import pytz
from pyrogram import enums, filters

from ValentinMusic import app
from ValentinMusic.core.mongo import mongodb

coupledb = mongodb.couples


def today_str():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d/%m/%Y")


def tomorrow_str():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    from datetime import timedelta
    tomorrow = now + timedelta(days=1)
    return tomorrow.strftime("%d/%m/%Y")



async def get_couple(chat_id, date):
    data = await coupledb.find_one({"chat_id": chat_id, "date": date})
    return data


async def save_couple(chat_id, date, c1_id, c2_id):
    await coupledb.update_one(
        {"chat_id": chat_id, "date": date},
        {"$set": {"c1_id": c1_id, "c2_id": c2_id}},
        upsert=True,
    )


@app.on_message(filters.command(["ship", "couple"]))
async def couple_func(_, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")

    m = await message.reply("💕 <b>Finding today's couple...</b>")
    chat_id = message.chat.id
    date = today_str()

    try:
        existing = await get_couple(chat_id, date)
        if existing:
            c1_id = int(existing["c1_id"])
            c2_id = int(existing["c2_id"])
            try:
                c1 = await app.get_users(c1_id)
                c2 = await app.get_users(c2_id)
                c1_name = c1.mention
                c2_name = c2.mention
            except Exception:
                c1_name = f"User {c1_id}"
                c2_name = f"User {c2_id}"

            text = (
                f"<b>💕 Couple of the Day:</b>\n\n"
                f"{c1_name} ❤️ {c2_name}\n\n"
                f"<i>New couple at 12 AM ({tomorrow_str()})</i>"
            )
            return await m.edit(text)

        # Pick new couple
        import asyncio
        await asyncio.sleep(2) # Realistic feeling delay
        
        members = []
        try:
            async for member in app.get_chat_members(chat_id, limit=200):
                if not member.user.is_bot and not member.user.is_deleted:
                    members.append(member.user.id)
        except Exception as e:
            return await m.edit(f"❌ <b>Error fetching members list!</b>\n\n<i>This command requires me to be an Admin with 'See Members' rights.</i>")

        if len(members) < 2:
            return await m.edit("❌ <b>Not enough members to perform shippering!</b>\n\n<i>Groups need at least 2 non-bot members.</i>")

        c1_id = random.choice(members)
        c2_id = random.choice(members)
        while c1_id == c2_id:
            c2_id = random.choice(members)

        await save_couple(chat_id, date, c1_id, c2_id)

        try:
            c1 = await app.get_users(c1_id)
            c2 = await app.get_users(c2_id)
            c1_mention = c1.mention
            c2_mention = c2.mention
        except Exception:
            c1_mention = f"User {c1_id}"
            c2_mention = f"User {c2_id}"

        text = (
            f"<b>💕 Couple of the Day:</b>\n\n"
            f"{c1_mention} ❤️ {c2_mention}\n\n"
            f"<i>New couple at 12 AM ({tomorrow_str()})</i>"
        )
        await m.edit(text)
    except Exception as e:
        await m.edit(f"❌ <b>Unexpected Error:</b> {str(e)}")
