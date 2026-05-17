from __future__ import annotations

import asyncio
from typing import Union

from ValentinMusic.misc import db
from ValentinMusic.utils.formatters import check_duration, seconds_to_min
from ValentinMusic.utils.stream.models import QueueItem
from config import autoclean, time_to_seconds


async def put_queue(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    user_id,
    stream,
    thumb=None,
    forceplay: Union[bool, str] = None,
):
    title = title.title()
    try:
        duration_in_seconds = time_to_seconds(duration) - 3
    except Exception:
        duration_in_seconds = 0
    item = QueueItem(
        title=title,
        dur=duration,
        streamtype=stream,
        by=user,
        user_id=user_id,
        chat_id=original_chat_id,
        file=file,
        vidid=vidid,
        thumb=thumb,
        seconds=duration_in_seconds,
        played=0,
    )
    if forceplay:
        check = db.get(chat_id)
        if check:
            check.insert(0, item)
        else:
            db[chat_id] = [item]
    else:
        db[chat_id].append(item)
    autoclean.append(file)


async def put_queue_index(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    stream,
    forceplay: Union[bool, str] = None,
):
    if "20.212.146.162" in vidid:
        try:
            dur = await asyncio.get_event_loop().run_in_executor(
                None, check_duration, vidid
            )
            duration = seconds_to_min(dur)
        except Exception:
            duration = "URL Stream"
            dur = 0
    else:
        dur = 0
    item = QueueItem(
        title=title,
        dur=duration,
        streamtype=stream,
        by=user,
        user_id=0,
        chat_id=original_chat_id,
        file=file,
        vidid=vidid,
        seconds=dur,
        played=0,
    )
    if forceplay:
        check = db.get(chat_id)
        if check:
            check.insert(0, item)
        else:
            db[chat_id] = [item]
    else:
        db[chat_id].append(item)
