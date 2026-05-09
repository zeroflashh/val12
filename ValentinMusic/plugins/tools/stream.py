from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.core.call import Anony
from ValentinMusic.utils.database import is_active_chat
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.utils.stream.stream import stream
from config import BANNED_USERS


@app.on_message(filters.command(["stream", "cstream"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def stream_cmd(client, message: Message, _, chat_id):
    if len(message.command) < 2:
        return await message.reply_text(_["str_1"])

    url = message.text.split(None, 1)[1].strip()
    
    if not await is_active_chat(chat_id):
        return await message.reply_text(_["general_5"])

    mystic = await message.reply_text(_["str_2"])

    try:
        await Anony.stream_call(url)
    except Exception as e:
        await mystic.edit_text(_["general_2"].format(type(e).__name__))
        return

    try:
        await stream(
            _,
            mystic,
            message.from_user.id,
            url,
            chat_id,
            message.from_user.first_name,
            message.chat.id,
            None,
            "index",
            None,
            None,
        )
    except Exception as e:
        await mystic.edit_text(_["general_2"].format(type(e).__name__))
        return

    await mystic.delete()
