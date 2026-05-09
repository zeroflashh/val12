"""
Info Module — Get detailed info about users and chats.
Ported from WilliamButcherBot (MIT License) by TheHamkerCat.
"""
import os

from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS


async def get_user_info(user, already=False):
    if not already:
        user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention("Link")
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    is_sudo = user_id in SUDOERS
    is_premium = getattr(user, "is_premium", False)
    is_bot = user.is_bot

    text = f"""<b>╔══════════════════╗
║       𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢
╠══════════════════╣
║ 𝗜𝗗:</b> <code>{user_id}</code>
<b>║ 𝗗𝗖:</b> {dc_id}
<b>║ 𝗡𝗮𝗺𝗲:</b> {first_name}
<b>║ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲:</b> @{username if username else 'None'}
<b>║ 𝗠𝗲𝗻𝘁𝗶𝗼𝗻:</b> {mention}
<b>║ 𝗦𝘂𝗱𝗼:</b> {'✅' if is_sudo else '❌'}
<b>║ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺:</b> {'✅' if is_premium else '❌'}
<b>║ 𝗕𝗼𝘁:</b> {'✅' if is_bot else '❌'}
<b>╚══════════════════╝</b>"""
    return [text, photo_id]


async def get_chat_info(chat, already=False):
    if not already:
        chat = await app.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type_ = str(chat.type).split(".")[-1]
    is_scam = getattr(chat, "is_scam", False)
    description = getattr(chat, "description", None) or "N/A"
    members = getattr(chat, "members_count", 0)
    dc_id = getattr(chat, "dc_id", "N/A")
    photo_id = chat.photo.big_file_id if chat.photo else None

    text = f"""<b>╔══════════════════╗
║       𝗖𝗛𝗔𝗧 𝗜𝗡𝗙𝗢
╠══════════════════╣
║ 𝗜𝗗:</b> <code>{chat_id}</code>
<b>║ 𝗗𝗖:</b> {dc_id}
<b>║ 𝗧𝘆𝗽𝗲:</b> {type_}
<b>║ 𝗧𝗶𝘁𝗹𝗲:</b> {title}
<b>║ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲:</b> @{username if username else 'None'}
<b>║ 𝗠𝗲𝗺𝗯𝗲𝗿𝘀:</b> {members}
<b>║ 𝗦𝗰𝗮𝗺:</b> {'✅' if is_scam else '❌'}
<b>║ 𝗗𝗲𝘀𝗰:</b> {description[:50] + '...' if len(description) > 50 else description}
<b>╚══════════════════╝</b>"""
    return [text, photo_id]


@app.on_message(filters.command("info"))
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if not user:
            return await message.reply_text("Can't get info of anonymous users.")
        user = user.id
    elif len(message.command) > 1:
        user = message.text.split(None, 1)[1]
    else:
        user = message.from_user.id

    m = await message.reply_text("🔍 <b>Fetching info...</b>")

    try:
        info_caption, photo_id = await get_user_info(user)
    except Exception as e:
        return await m.edit(f"Error: {str(e)}\nPerhaps you meant to use /chat_info ?")

    if not photo_id:
        return await m.edit(info_caption, disable_web_page_preview=True)
    photo = await app.download_media(photo_id)
    await message.reply_photo(photo, caption=info_caption, quote=False)
    await m.delete()
    os.remove(photo)


@app.on_message(filters.command("chat_info"))
async def chat_info_func(_, message: Message):
    if len(message.command) == 1:
        chat = message.chat.id
        if chat == message.from_user.id:
            return await message.reply_text("**Usage:** /chat_info [USERNAME|ID]")
    else:
        chat = message.text.split(None, 1)[1]
    try:
        m = await message.reply_text("🔍 <b>Fetching chat info...</b>")
        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)
        photo = await app.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)
        await m.delete()
        os.remove(photo)
    except Exception as e:
        await m.edit(f"Error: {str(e)}")
