from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from ValentinMusic import app
from ValentinMusic.utils.database import is_music_playing
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.utils.inline.play import volume_markup
from strings import get_string
from config import BANNED_USERS


@app.on_message(filters.command(["volume", "cvolume"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def volume_set(client, message: Message, _, chat_id):
    if len(message.command) == 1:
        if not await is_music_playing(chat_id):
            return await message.reply_text(_["admin_1"])
        return await message.reply_text(
            "🔊 <b>Volume Control</b>\n\nTap a button to set volume:",
            reply_markup=InlineKeyboardMarkup(volume_markup(_))
        )

    volume = message.text.split(None, 1)[1].strip()
    if not volume.isdigit():
        return await message.reply_text("<b>Usage:</b> /volume [1-200]")

    volume = int(volume)
    if volume < 1 or volume > 200:
        return await message.reply_text("<b>Volume must be between 1 and 200.</b>")

    from ValentinMusic.core.call import Anony
    from ValentinMusic.utils.database import group_assistant

    assistant = await group_assistant(Anony, chat_id)
    try:
        await assistant.change_volume_call(chat_id, volume)
        await message.reply_text(
            f"🔊 <b>Volume set to</b> `{volume}%`",
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to set volume: {e}")
