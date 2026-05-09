from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.core.call import Anony
from ValentinMusic.utils.database import set_loop
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.utils.inline import close_markup
from config import BANNED_USERS


from ValentinMusic.utils.functions import delete_after_10
import asyncio

@app.on_message(
    filters.command(["end", "stop", "cend", "cstop"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    await Anony.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    m = await message.reply_text(
        _["admin_5"].format(message.from_user.first_name), reply_markup=close_markup(_)
    )
    asyncio.create_task(delete_after_10(m))
