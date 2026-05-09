from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.misc import db
from ValentinMusic.utils.database import get_loop, set_loop
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(filters.command(["loop", "cloop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def loop_cmd(client, message: Message, _, chat_id):
    usage = """<b>Usage:</b> /loop [1-10] or [enable] or [disable]

<b>Examples:</b>
  /loop 3 - repeat current track 3 times
  /loop enable - repeat indefinitely (10 times)
  /loop disable - stop looping"""
    
    if len(message.command) != 2:
        return await message.reply_text(usage)
    
    state = message.text.split(None, 1)[1].strip().lower()
    
    # Check if there's something playing
    check = db.get(chat_id)
    if not check or len(check) == 0:
        return await message.reply_text("» No track playing to loop.")
    
    if state.isdigit():
        state = int(state)
        if 1 <= state <= 10:
            got = await get_loop(chat_id)
            if got != 0:
                state = got + state
            if int(state) > 10:
                state = 10
            await set_loop(chat_id, state)
            return await message.reply_text(
                f"🔁 <b>Loop enabled for</b> {state} <b>times.</b>",
                reply_markup=close_markup(_),
            )
        else:
            return await message.reply_text(usage)
    elif state == "enable":
        await set_loop(chat_id, 10)
        return await message.reply_text(
            "🔁 <b>Loop enabled indefinitely.</b>",
            reply_markup=close_markup(_),
        )
    elif state == "disable":
        await set_loop(chat_id, 0)
        return await message.reply_text(
            "🔁 <b>Loop disabled.</b>",
            reply_markup=close_markup(_),
        )
    else:
        return await message.reply_text(usage)
