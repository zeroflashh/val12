import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ValentinMusic import YouTube, app
from ValentinMusic.core.call import Anony
from ValentinMusic.misc import SUDOERS, db
from ValentinMusic.utils.database import (
    get_active_chats,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from ValentinMusic.utils.decorators.language import languageCB
from ValentinMusic.utils.formatters import seconds_to_min
from ValentinMusic.utils.inline import close_markup, stream_markup, stream_markup_timer
from ValentinMusic.utils.stream.autoclear import auto_clean
from ValentinMusic.utils.stream.resolve import skip_resolved_item, send_now_playing
from ValentinMusic.utils.thumbnails import get_thumb
from config import (
    BANNED_USERS,
    SUPPORT_CHAT,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    adminlist,
    confirmer,
    votemode,
)
from strings import get_string
from ValentinMusic.utils.functions import delete_after_10

checker = {}
upvoters = {}


@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
        counter = bet[1]
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    mention = CallbackQuery.from_user.first_name
    if command == "UpVote":
        if chat_id not in votemode:
            votemode[chat_id] = {}
        if chat_id not in upvoters:
            upvoters[chat_id] = {}

        voters = (upvoters[chat_id]).get(CallbackQuery.message.id)
        if not voters:
            upvoters[chat_id][CallbackQuery.message.id] = []

        vote = (votemode[chat_id]).get(CallbackQuery.message.id)
        if not vote:
            votemode[chat_id][CallbackQuery.message.id] = 0

        if CallbackQuery.from_user.id in upvoters[chat_id][CallbackQuery.message.id]:
            (upvoters[chat_id][CallbackQuery.message.id]).remove(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] -= 1
        else:
            (upvoters[chat_id][CallbackQuery.message.id]).append(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] += 1
        upvote = await get_upvote_count(chat_id)
        get_upvotes = int(votemode[chat_id][CallbackQuery.message.id])
        if get_upvotes >= upvote:
            votemode[chat_id][CallbackQuery.message.id] = upvote
            try:
                exists = confirmer[chat_id][CallbackQuery.message.id]
                current = db[chat_id][0]
            except (KeyError, IndexError):
                return await CallbackQuery.edit_message_text(f"ғᴀɪʟᴇᴅ.")
            try:
                if current["vidid"] != exists["vidid"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
                if current["file"] != exists["file"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
            except Exception:
                return await CallbackQuery.edit_message_text(_["admin_36"])
            try:
                await CallbackQuery.edit_message_text(_["admin_37"].format(upvote))
            except Exception:
                pass
            command = counter
            mention = "ᴜᴘᴠᴏᴛᴇs"
        else:
            if (
                CallbackQuery.from_user.id
                in upvoters[chat_id][CallbackQuery.message.id]
            ):
                await CallbackQuery.answer(_["admin_38"], show_alert=True)
            else:
                await CallbackQuery.answer(_["admin_39"], show_alert=True)
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"👍 {get_upvotes}",
                            callback_data=f"ADMIN  UpVote|{chat_id}_{counter}",
                        )
                    ]
                ]
            )
            await CallbackQuery.answer(_["admin_40"], show_alert=True)
            return await CallbackQuery.edit_message_reply_markup(reply_markup=upl)
    else:
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            if CallbackQuery.from_user.id not in SUDOERS:
                admins = adminlist.get(CallbackQuery.message.chat.id)
                if not admins:
                    return await CallbackQuery.answer(_["admin_13"], show_alert=True)
                else:
                    if CallbackQuery.from_user.id not in admins:
                        return await CallbackQuery.answer(
                            _["admin_14"], show_alert=True
                        )
    if command == "Pause":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_1"], show_alert=True)
        await CallbackQuery.answer()
        await music_off(chat_id)
        await Anony.pause_stream(chat_id)

        # Update Player caption with pause indicator
        try:
            check = db.get(chat_id)
            if check:
                vidid = check[0].get("vidid")
                title = check[0].get("title")
                duration = check[0].get("dur")
                user = check[0].get("by")
                streamtype = check[0].get("streamtype")
                img = check[0].get("thumb")
                if vidid == "telegram":
                    img = TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else TELEGRAM_VIDEO_URL
                elif vidid == "soundcloud":
                    img = SOUNCLOUD_IMG_URL
                if not img:
                    img = TELEGRAM_AUDIO_URL
                caption = _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration,
                    user,
                )
                caption += f"\n\n<blockquote>▶️ Stream paused by {CallbackQuery.from_user.mention}</blockquote>"
                from pyrogram.types import InputMediaPhoto
                await CallbackQuery.edit_message_media(
                    media=InputMediaPhoto(media=img, caption=caption),
                    reply_markup=CallbackQuery.message.reply_markup
                )
        except Exception as e:
            print(f"Update Player Error: {e}")

        m = await CallbackQuery.message.reply_text(
            _["admin_2"].format(mention), reply_markup=close_markup(_)
        )
        asyncio.create_task(delete_after_10(m))
    elif command == "Resume":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_3"], show_alert=True)
        await CallbackQuery.answer()
        await music_on(chat_id)
        await Anony.resume_stream(chat_id)

        # Update Player caption with resume indicator
        try:
            check = db.get(chat_id)
            if check:
                vidid = check[0].get("vidid")
                title = check[0].get("title")
                duration = check[0].get("dur")
                user = check[0].get("by")
                streamtype = check[0].get("streamtype")
                img = check[0].get("thumb")
                if vidid == "telegram":
                    img = TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else TELEGRAM_VIDEO_URL
                elif vidid == "soundcloud":
                    img = SOUNCLOUD_IMG_URL
                if not img:
                    img = TELEGRAM_AUDIO_URL
                caption = _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration,
                    user,
                )
                caption += f"\n\n<blockquote>▶️ Stream resumed by {CallbackQuery.from_user.mention}</blockquote>"
                from pyrogram.types import InputMediaPhoto
                await CallbackQuery.edit_message_media(
                    media=InputMediaPhoto(media=img, caption=caption),
                    reply_markup=CallbackQuery.message.reply_markup
                )
        except Exception as e:
            print(f"Update Player Error: {e}")

        m = await CallbackQuery.message.reply_text(
            _["admin_4"].format(mention), reply_markup=close_markup(_)
        )
        asyncio.create_task(delete_after_10(m))
    elif command == "Stop" or command == "End":
        await CallbackQuery.answer()
        await Anony.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        m = await CallbackQuery.message.reply_text(
            _["admin_5"].format(mention), reply_markup=close_markup(_)
        )
        asyncio.create_task(delete_after_10(m))
        await CallbackQuery.message.delete()
    elif command == "Skip" or command == "Replay":
        check = db.get(chat_id)
        if not check:
            return await CallbackQuery.answer(_["admin_21"], show_alert=True)
        if command == "Skip":
            txt = f"➻ Stream Skipped by: {mention}"
            popped = None
            try:
                popped = check.pop(0)
                if popped:
                    await auto_clean(popped)
                if not check:
                    await CallbackQuery.edit_message_text(
                        f"➻ Stream Skipped by: {mention}"
                    )
                    m = await CallbackQuery.message.reply_text(
                        text=_["admin_6"].format(
                            mention, CallbackQuery.message.chat.title
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
                    await CallbackQuery.edit_message_text(
                        f"➻ Stream SKi pped by: {mention}"
                    )
                    m = await CallbackQuery.message.reply_text(
                        text=_["admin_6"].format(
                            mention, CallbackQuery.message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    asyncio.create_task(delete_after_10(m))
                    return await Anony.stop_stream(chat_id)
                except Exception:
                    return
        else:
            txt = f"➻ Stream re-played by: {mention}"
        if not check:
            return await CallbackQuery.answer(_["admin_21"], show_alert=True)
        await CallbackQuery.answer()
        m = await CallbackQuery.message.reply_text(txt)
        asyncio.create_task(delete_after_10(m))
        queued = check[0]["file"]
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        duration = check[0]["dur"]
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
        try:
            if "vid_" in queued:
                async def _mk():
                    return await CallbackQuery.message.reply_text(
                        _["call_7"], disable_web_page_preview=True,
                    )
                file_or_link, image, mystic_msg = await skip_resolved_item(
                    chat_id, queued, videoid, status, make_mystic=_mk,
                )
            else:
                file_or_link, image, mystic_msg = await skip_resolved_item(
                    chat_id, queued, videoid, status,
                )
        except Exception:
            err_key = "admin_7" if "live_" in queued else "call_6"
            err_msg = _[err_key].format(title) if err_key == "admin_7" else _[err_key]
            return await CallbackQuery.message.reply_text(
                err_msg, reply_markup=close_markup(_),
            )

        await send_now_playing(
            CallbackQuery.message, chat_id, _, videoid, title,
            duration, user, streamtype, thumb=image, queued=queued,
        )
        if mystic_msg:
            await mystic_msg.delete()
        await CallbackQuery.edit_message_text(txt, reply_markup=close_markup(_))


async def markup_timer():
    while not await asyncio.sleep(7):
        active_chats = await get_active_chats()
        for chat_id in active_chats:
            try:
                if not await is_music_playing(chat_id):
                    continue
                playing = db.get(chat_id)
                if not playing:
                    continue
                duration_seconds = int(playing[0]["seconds"])
                if duration_seconds == 0:
                    continue
                try:
                    mystic = playing[0]["mystic"]
                except (IndexError, KeyError, TypeError):
                    continue
                try:
                    check = checker[chat_id][mystic.id]
                    if check is False:
                        continue
                except (KeyError, AttributeError):
                    pass
                try:
                    language = await get_lang(chat_id)
                    _ = get_string(language)
                except Exception:
                    _ = get_string("en")
                try:
                    buttons = stream_markup_timer(
                        _,
                        chat_id,
                        seconds_to_min(playing[0]["played"]),
                        playing[0]["dur"],
                    )
                    await mystic.edit_reply_markup(
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                except Exception:
                    continue
            except Exception:
                continue


asyncio.create_task(markup_timer())


@app.on_callback_query(filters.regex(r"^volume ") & ~BANNED_USERS)
@languageCB
async def volume_callback(client, CallbackQuery, _):
    # Check if user is admin or sudo
    is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
    if not is_non_admin:
        if CallbackQuery.from_user.id not in SUDOERS:
            admins = adminlist.get(CallbackQuery.message.chat.id)
            if not admins:
                return await CallbackQuery.answer(_["admin_13"], show_alert=True)
            if CallbackQuery.from_user.id not in admins:
                return await CallbackQuery.answer(_["admin_14"], show_alert=True)

    chat_id = CallbackQuery.message.chat.id
    vol = CallbackQuery.data.split()[1]

    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)

    if not await is_music_playing(chat_id):
        return await CallbackQuery.answer(_["admin_1"], show_alert=True)

    try:
        vol = int(vol)
    except (ValueError, TypeError):
        return await CallbackQuery.answer("Invalid volume.", show_alert=True)

    from ValentinMusic.core.call import Anony
    from ValentinMusic.utils.database import group_assistant

    assistant = await group_assistant(Anony, chat_id)
    try:
        await assistant.change_volume_call(chat_id, vol)
        await CallbackQuery.answer(f"Volume set to {vol}%", show_alert=True)
    except Exception as e:
        await CallbackQuery.answer(f"Failed: {str(e)}", show_alert=True)
