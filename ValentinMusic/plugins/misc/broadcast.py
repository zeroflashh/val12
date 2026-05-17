import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS
from ValentinMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from ValentinMusic.utils.decorators.language import language
from ValentinMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False


@app.on_message(filters.command(["broadcast", "gcast"]) & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-assistant" in query:
            query = query.replace("-assistant", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query.strip() == "":
            return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    
    # Flags
    pin_msg = "-pin" in message.text
    pin_loud = "-pinloud" in message.text
    no_bot = "-nobot" in message.text
    assistant_broad = "-assistant" in message.text
    user_broad = "-user" in message.text
    
    # Broadcast to chats
    if not no_bot:
        sent = 0
        pin = 0
        await message.reply_text(_["broad_1"])
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                if pin_msg:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        pass
                elif pin_loud:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        pass
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(int(fw.value))
            except Exception:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except Exception:
            pass

    # Broadcast to users
    if user_broad:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(int(fw.value))
            except Exception:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except Exception:
            pass

    # Broadcast via assistants
    if assistant_broad:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from ValentinMusic.core.userbot import assistants
        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    await client.forward_messages(
                        dialog.chat.id, y, x
                    ) if message.reply_to_message else await client.send_message(
                        dialog.chat.id, text=query
                    )
                    sent += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    await asyncio.sleep(int(fw.value))
                except Exception:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except Exception:
            pass
    IS_BROADCASTING = False


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except Exception:
            continue


asyncio.create_task(auto_clean())
