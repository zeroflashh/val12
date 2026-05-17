from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from ValentinMusic import YouTube, app
from ValentinMusic.core.call import Anony
from ValentinMusic.misc import db
from ValentinMusic.utils.database import get_loop
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.utils.inline import close_markup, stream_markup
from ValentinMusic.utils.stream.autoclear import auto_clean
from ValentinMusic.utils.thumbnails import get_thumb
from config import BANNED_USERS
from ValentinMusic.utils.functions import delete_after_10
import asyncio

from ValentinMusic.utils.stream.resolve import skip_resolved_item, send_now_playing


@app.on_message(
    filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_8"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                            except (IndexError, KeyError):
                                return await message.reply_text(_["admin_12"])
                            if popped:
                                await auto_clean(popped)
                            if not check:
                                try:
                                    m = await message.reply_text(
                                        text=_["admin_6"].format(
                                            message.from_user.first_name,
                                            message.chat.title,
                                        ),
                                        reply_markup=close_markup(_),
                                    )
                                    asyncio.create_task(delete_after_10(m))
                                    await Anony.stop_stream(chat_id)
                                except Exception:
                                    return
                                break
                    else:
                        return await message.reply_text(_["admin_11"].format(count))
                else:
                    return await message.reply_text(_["admin_10"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_9"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                await auto_clean(popped)
            if not check:
                m = await message.reply_text(
                    text=_["admin_6"].format(
                        message.from_user.first_name, message.chat.title
                    ),
                    reply_markup=close_markup(_),
                )
                asyncio.create_task(delete_after_10(m))
                try:
                    return await Anony.stop_stream(chat_id)
                except Exception:
                    return
        except (IndexError, KeyError):
            try:
                m = await message.reply_text(
                    text=_["admin_6"].format(
                        message.from_user.first_name, message.chat.title
                    ),
                    reply_markup=close_markup(_),
                )
                asyncio.create_task(delete_after_10(m))
                return await Anony.stop_stream(chat_id)
            except Exception:
                return
    m = await message.reply_text(f"➻ Stream Skipped by: {message.from_user.first_name}")
    asyncio.create_task(delete_after_10(m))
    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    db[chat_id][0]["played"] = 0
    exis = (check[0]).get("old_dur")
    if exis:
        db[chat_id][0]["dur"] = exis
        db[chat_id][0]["seconds"] = check[0]["old_second"]
        db[chat_id][0]["speed_path"] = None
        db[chat_id][0]["speed"] = 1.0

    mystic = None
    try:
        if "vid_" in queued:
            async def _mk():
                return await message.reply_text(_["call_7"], disable_web_page_preview=True)
            file_or_link, image, mystic = await skip_resolved_item(
                chat_id, queued, videoid, status, make_mystic=_mk,
            )
        else:
            file_or_link, image, _ = await skip_resolved_item(
                chat_id, queued, videoid, status,
            )
    except Exception:
        err_key = "admin_7" if "live_" in queued else "call_6"
        err_msg = _[err_key].format(title) if err_key == "admin_7" else _[err_key]
        return await message.reply_text(err_msg)

    await send_now_playing(
        message, chat_id, _, videoid, title, check[0]["dur"], user, streamtype,
        thumb=image, queued=queued,
    )
    if mystic:
        await mystic.delete()
