from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.core.call import Anony
from ValentinMusic.utils.database import is_music_playing, music_on
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.utils.inline import close_markup
from config import BANNED_USERS


from ValentinMusic.utils.functions import delete_after_10
import asyncio

@app.on_message(filters.command(["resume", "cresume"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def resume_com(cli, message: Message, _, chat_id):
    if await is_music_playing(chat_id):
        return await message.reply_text(_["admin_3"])
    await music_on(chat_id)
    await Anony.resume_stream(chat_id)
    m = await message.reply_text(
        _["admin_4"].format(message.from_user.first_name), reply_markup=close_markup(_)
    )
    asyncio.create_task(delete_after_10(m))
