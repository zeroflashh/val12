import os
import aiohttp
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from ValentinMusic import YouTube, app
from ValentinMusic.utils.database import get_lang
from strings import get_string
from config import BANNED_USERS


def format_duration(dur):
    if not dur or ":" not in str(dur):
        return dur
    parts = str(dur).split(":")
    try:
        if len(parts) == 2:
            return f"{int(parts[0]):02d}:{int(parts[1]):02d} min"
        elif len(parts) == 3:
            return f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d} hours"
    except:
        pass
    return dur


@app.on_message(filters.command(["ytdl", "song"]) & ~BANNED_USERS)
async def ytdl_command_handler(client, message: Message):
    chat_id = message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)

    if len(message.command) < 2:
        return await message.reply_text(
            _["ytdl_1"] if "ytdl_1" in _ else "<b>Usage:</b> /song [name or YouTube link]"
        )

    query = message.text.split(None, 1)[1]

    # Check if it's a YouTube URL
    is_url = False
    if "youtube.com" in query or "youtu.be" in query:
        is_url = True

    if "playlist" in query or "list=" in query:
        return await message.reply_text(
            _["ytdl_2"] if "ytdl_2" in _ else "<b>Playlists not supported.</b>"
        )

    m = await message.reply_text(
        "<b>🔍 Searching...</b>"
    )

    try:
        results = await YouTube.search(query, limit=10)
        if not results:
            return await m.edit(_["ytdl_4"] if "ytdl_4" in _ else "<b>No results found.</b>")

        # If it's a direct URL, process directly
        if is_url:
            vidid = results[0]["id"]
            title = results[0]["title"]
            duration = format_duration(results[0]["duration"])

            buttons = [
                [
                    InlineKeyboardButton(text="Audio 🎵", callback_data=f"ytdl_audio|{vidid}"),
                    InlineKeyboardButton(text="Video 📹", callback_data=f"ytdl_video_choice|{vidid}"),
                ],
                [
                    InlineKeyboardButton(text="Close", callback_data="close"),
                ],
            ]
            return await m.edit(
                f"<b>🎬 Title:</b> {title}\n<b>⏱ Duration:</b> {duration}\n\nSelect format:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        # Show first 5 results (page 1)
        text = f"<b>🔍 Search results for:</b> {query}\n\n"
        buttons = []
        row = []

        for i, result in enumerate(results[:5], 1):
            title = result["title"][:50] + "..." if len(result["title"]) > 50 else result["title"]
            duration = result["duration"] or "Unknown"
            vidid = result["id"]
            text += f"<b>{i}.</b> {title} [{duration}]\n"
            row.append(InlineKeyboardButton(text=str(i), callback_data=f"ytdl_select|{vidid}"))

        buttons.append(row)
        buttons.append([InlineKeyboardButton(text="Next ➡️", callback_data=f"ytdl_page|{query}|1")])
        buttons.append([InlineKeyboardButton(text="Close", callback_data="close")])

        await m.edit(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

    except Exception as e:
        await m.edit(_["ytdl_10"].format(query, str(e)) if "ytdl_10" in _ else f"<b>Error:</b> {str(e)}")


@app.on_callback_query(filters.regex(r"^ytdl_page\|") & ~BANNED_USERS)
async def ytdl_pagination(client, query: CallbackQuery):
    try:
        data = query.data.split("|")
        query_text = data[1]
        page = int(data[2])

        m = await query.message.edit("<b>🔍 Loading next page...</b>")

        results = await YouTube.search(query_text, limit=10)
        if not results:
            return await query.answer("No more results.", show_alert=True)

        start = 5 if page == 1 else 0
        end = 10 if page == 1 else 5
        display_results = results[start:end]

        text = f"<b>🔍 Search results for:</b> {query_text}\n<b>Page {page + 1}/2</b>\n\n"
        buttons = []
        row = []

        for i, result in enumerate(display_results, start + 1):
            title = result["title"][:50] + "..." if len(result["title"]) > 50 else result["title"]
            duration = result["duration"] or "Unknown"
            vidid = result["id"]
            text += f"<b>{i}.</b> {title} [{duration}]\n"
            row.append(InlineKeyboardButton(text=str(i), callback_data=f"ytdl_select|{vidid}"))

        buttons.append(row)
        prev_page = 0 if page == 1 else 1
        buttons.append([InlineKeyboardButton(text="⬅️ Previous", callback_data=f"ytdl_page|{query_text}|{prev_page}")])
        buttons.append([InlineKeyboardButton(text="Close", callback_data="close")])

        await m.edit(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


@app.on_callback_query(filters.regex(r"^ytdl_select\|") & ~BANNED_USERS)
async def ytdl_select(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    vidid = query.data.split("|")[1]

    try:
        title, duration, duration_sec, thumb, vidid, channel = await YouTube.details(vidid, True)
        duration_fmt = format_duration(duration)

        buttons = [
            [
                InlineKeyboardButton(text="Audio 🎵", callback_data=f"ytdl_audio|{vidid}"),
                InlineKeyboardButton(text="Video 📹", callback_data=f"ytdl_video_choice|{vidid}"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Results", callback_data="ytdl_back_search"),
                InlineKeyboardButton(text="Close", callback_data="close"),
            ],
        ]

        await query.message.edit(
            f"<b>🎬 Selected:</b> {title}\n<b>⏱ Duration:</b> {duration_fmt}\n<b>📺 Channel:</b> {channel}\n\nSelect format:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


@app.on_callback_query(filters.regex("ytdl_back_search") & ~BANNED_USERS)
async def ytdl_back_to_search(client, query: CallbackQuery):
    # Get the last search query from the message text or use a default
    # For simplicity, we just show the last 5 results again
    try:
        text = query.message.text
        # Extract the query from the previous message if available
        await query.message.edit("<b>🔍 Searching...</b>")
        # Re-show search results - for now just acknowledge
        await query.message.edit(
            "<b>Select a song from the previous results.</b>\n\n<i>Use /song command again to search for a new song.</i>"
        )
    except:
        pass


@app.on_callback_query(filters.regex("ytdl_audio") & ~BANNED_USERS)
async def ytdl_audio_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    vidid = query.data.split("|")[1]

    await query.message.edit(_["ytdl_6"] if "ytdl_6" in _ else "<b>Downloading audio...</b>")

    try:
        url = f"https://www.youtube.com/watch?v={vidid}"
        title, duration, duration_sec, thumb, vidid, channel = await YouTube.details(vidid, True)
        duration = format_duration(duration)

        thumb_path = f"downloads/thumb_{vidid}.jpg"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumb) as resp:
                    if resp.status == 200:
                        with open(thumb_path, "wb") as f:
                            f.write(await resp.read())
                    else:
                        thumb_path = None
        except:
            thumb_path = None

        file_path, direct = await YouTube.download(url, query.message, songaudio=True, title=title)

        caption = _["ytdl_8"].format(title, duration, "320 kbps", app.username) if "ytdl_8" in _ else f"<b>Title:</b> {title}\n<b>Duration:</b> {duration}\n<b>Quality:</b> 320 kbps\n\n<b>Via:</b> @{app.username}"

        await client.send_audio(
            chat_id=query.message.chat.id,
            audio=file_path,
            caption=caption,
            title=title,
            performer=channel if channel else "Val12 Player",
            duration=duration_sec,
            thumb=thumb_path
        )
        await query.message.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        await query.message.edit(_["ytdl_10"].format(vidid, str(e)) if "ytdl_10" in _ else f"<b>Error:</b> {str(e)}")


@app.on_callback_query(filters.regex("ytdl_video_choice") & ~BANNED_USERS)
async def ytdl_video_choice_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    vidid = query.data.split("|")[1]
    url = f"https://www.youtube.com/watch?v={vidid}"

    await query.message.edit(_["ytdl_7"] if "ytdl_7" in _ else "<b>Fetching video qualities...</b>")

    try:
        opus_size, vp9_size, av1_size, vp9_id, av1_id = await YouTube.get_ytdl_formats(url)
        title, duration, duration_sec, thumb, vidid, channel = await YouTube.details(vidid, True)
        duration = format_duration(duration)

        buttons = [
            [
                InlineKeyboardButton(text=f"720p ({vp9_size})", callback_data=f"ytdl_download|{vidid}|video|{vp9_id}|720p"),
                InlineKeyboardButton(text=f"480p ({av1_size})", callback_data=f"ytdl_download|{vidid}|video|{av1_id}|480p"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Back", callback_data=f"ytdl_audio|{vidid}"),
                InlineKeyboardButton(text="Close", callback_data="close"),
            ],
        ]

        await query.message.edit(
            f"<b>🎬 Title:</b> {title}\n<b>⏱ Duration:</b> {duration}\n\nSelect quality:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        await query.message.edit(_["ytdl_10"].format("qualities", str(e)) if "ytdl_10" in _ else f"<b>Error:</b> {str(e)}")


@app.on_callback_query(filters.regex("ytdl_download") & ~BANNED_USERS)
async def ytdl_download_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    data = query.data.split("|")
    vidid = data[1]
    ftype = data[2]
    fid = data[3]
    quality = data[4] if len(data) > 4 else "Unknown"

    await query.message.edit(_["ytdl_9"].format(quality, quality) if "ytdl_9" in _ else f"<b>Downloading {quality} video...</b>")

    try:
        url = f"https://www.youtube.com/watch?v={vidid}"
        title, duration, duration_sec, thumb, vidid, channel = await YouTube.details(vidid, True)
        duration = format_duration(duration)

        thumb_path = f"downloads/thumb_{vidid}.jpg"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumb) as resp:
                    if resp.status == 200:
                        with open(thumb_path, "wb") as f:
                            f.write(await resp.read())
                    else:
                        thumb_path = None
        except:
            thumb_path = None

        if ftype == "video":
            file_path, direct = await YouTube.download(url, query.message, songvideo=True, format_id=fid, title=title)

        caption = (
            f"<b>Title:</b> {title}\n\n"
            f"<b>Duration:</b> {duration}\n"
            f"<b>Quality:</b> {quality}\n\n"
            f"<b>Via:</b> @{app.username}"
        )

        if ftype == "video":
            await client.send_video(
                chat_id=query.message.chat.id,
                video=file_path,
                caption=caption,
                duration=duration_sec,
                thumb=thumb_path
            )
        await query.message.delete()

        if os.path.exists(file_path):
            os.remove(file_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        await query.message.edit(_["ytdl_10"].format(ftype, str(e)) if "ytdl_10" in _ else f"<b>Error:</b> {str(e)}")