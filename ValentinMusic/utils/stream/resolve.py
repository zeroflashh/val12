from typing import Any

from ValentinMusic import YouTube
from ValentinMusic.core.call import Anony
from ValentinMusic.utils.exceptions import AssistantErr
from ValentinMusic.utils.thumbnails import get_thumb


async def _safe_thumbnail(videoid: str) -> Any | None:
    try:
        return await YouTube.thumbnail(videoid, True)
    except Exception:
        return None


async def _resolve_thumb(videoid: str, queued: str) -> str | None:
    """Get thumbnail for a resolved stream item."""
    if videoid == "telegram":
        return None
    if videoid == "soundcloud":
        return None
    thumb = await get_thumb(videoid)
    return thumb if thumb and not thumb.startswith("http") else await get_thumb(videoid)


async def skip_resolved_item(
    chat_id: int,
    queued: str,
    videoid: str,
    status: bool | None,
    make_mystic=None,
):
    """Resolve a queue item and skip to it.
    
    Args:
        make_mystic: optional async callable() -> Message for download progress
    
    Returns:
        (file_or_link, image_or_None, mystic_or_None)
    
    Raises:
        AssistantErr on any failure
    """
    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            raise AssistantErr("live_not_found")
        image = await _safe_thumbnail(videoid)
        await Anony.skip_stream(chat_id, link, video=status, image=image)
        return link, image, None

    if "vid_" in queued:
        mystic = await make_mystic() if make_mystic else None
        file_path, direct = await YouTube.download(
            videoid, mystic, videoid=True, video=status,
        )
        image = await _safe_thumbnail(videoid)
        await Anony.skip_stream(chat_id, file_path, video=status, image=image)
        return file_path, image, mystic

    if "index_" in queued:
        await Anony.skip_stream(chat_id, videoid, video=status)
        return videoid, None, None

    image = await _safe_thumbnail(videoid) if videoid not in ("telegram", "soundcloud") else None
    await Anony.skip_stream(chat_id, queued, video=status, image=image)
    return queued, image, None


async def send_now_playing(
    send_target,
    chat_id: int,
    _,
    videoid: str,
    title: str,
    duration: str,
    user: str,
    streamtype: str,
    thumb: str | None = None,
    queued: str | None = None,
):
    """Send 'now playing' photo notification and update DB.

    Returns the sent message.
    """
    from ValentinMusic import app
    from ValentinMusic.misc import db
    from ValentinMusic.utils.inline.play import stream_markup
    from pyrogram.types import InlineKeyboardMarkup
    import config

    button = stream_markup(_, chat_id)
    is_index = "index_" in (queued or "")

    if is_index:
        img = config.STREAM_IMG_URL
        caption = _["stream_2"].format(user)
        markup = "tg"
    elif videoid == "telegram":
        img = config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL
        caption = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], duration, user)
        markup = "tg"
    elif videoid == "soundcloud":
        img = config.SOUNCLOUD_IMG_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL
        caption = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], duration, user)
        markup = "tg"
    else:
        img = thumb or await get_thumb(videoid)
        caption = _["stream_1"].format(
            f"https://t.me/{app.username}?start=info_{videoid}",
            title[:23], duration, user,
        )
        markup = "stream" if "vid_" in (queued or "") else "tg"

    run = await send_target.reply_photo(
        photo=img,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(button),
    )

    if db.get(chat_id):
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = markup

    return run
