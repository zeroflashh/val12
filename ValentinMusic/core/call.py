import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import Update
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from pytgcalls.types.stream import StreamEnded
from ntgcalls import ConnectionNotFound, TelegramServerError, ConnectionError, RTMPStreamingUnsupported

import config
from ValentinMusic import LOGGER, YouTube, app
from ValentinMusic.misc import db
from ValentinMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ValentinMusic.utils.exceptions import AssistantErr
from ValentinMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from ValentinMusic.utils.inline.play import stream_markup
from ValentinMusic.utils.stream.autoclear import auto_clean
from ValentinMusic.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


def _build_stream(media_path, video=True, extra_params=None):
    params = dict(media_path=media_path, audio_parameters=AudioQuality.HIGH)
    if video:
        params.update(
            video_parameters=VideoQuality.SD_480p,
            audio_flags=MediaStream.Flags.REQUIRED,
            video_flags=MediaStream.Flags.REQUIRED,
        )
    else:
        params.update(audio_flags=MediaStream.Flags.REQUIRED)
    if extra_params:
        params.update(extra_params)
    return MediaStream(**params)


_CALL_ATTRS = ["one", "two", "three", "four", "five"]

class Call(PyTgCalls):
    def __init__(self):
        from ValentinMusic import userbot

        self.clients: list[PyTgCalls | None] = []
        for idx, attr in enumerate(_CALL_ATTRS, start=1):
            ub = getattr(userbot, attr, None)
            client = PyTgCalls(ub) if ub else None
            self.clients.append(client)
            setattr(self, attr, client)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except Exception:
            pass

    async def stop_stream_force(self, chat_id: int):
        for ref in self.clients:
            if ref:
                try:
                    await ref.leave_call(chat_id)
                except Exception:
                    pass
        try:
            await _clear_(chat_id)
        except Exception:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                vs = {"0.5": 2.0, "0.75": 1.35, "1.5": 0.68, "2.0": 0.5}.get(str(speed), 1.0)
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
            else:
                pass
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        is_video = playing[0]["streamtype"] == "video"
        extra = {"ffmpeg_parameters": f"-ss {played} -to {duration}"}
        stream = _build_stream(out, video=is_video, extra_params=extra) if is_video else MediaStream(
            media_path=out,
            audio_parameters=AudioQuality.HIGH,
            audio_flags=MediaStream.Flags.REQUIRED,
            video_flags=MediaStream.Flags.IGNORE,
            ffmpeg_parameters=f"-ss {played} -to {duration}",
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            try:
                await assistant.play(chat_id, stream)
            except (ConnectionNotFound, TelegramServerError, ConnectionError):
                raise AssistantErr("Telegram server error during speed change")
            except Exception as e:
                raise AssistantErr(f"Speed change failed: {e}")
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            if check:
                check.pop(0)
        except Exception:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except Exception:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)

        if not link.startswith("http"):
            abs_link = os.path.abspath(link)
            found_path = None
            for ext in ['.mp4', '.webm', '.m4a', '.mkv', '.mp3']:
                test_path = abs_link
                for remove_ext in ['.mp4', '.m4a', '.webm', '.mkv', '.mp3']:
                    test_path = test_path.replace(remove_ext, ext)
                if os.path.exists(test_path):
                    found_path = test_path
                    break
            if not found_path:
                dir_path = os.path.dirname(abs_link)
                base_name = os.path.splitext(os.path.basename(abs_link))[0]
                for f in os.listdir(dir_path) if os.path.exists(dir_path) else []:
                    if f.startswith(base_name):
                        found_path = os.path.join(dir_path, f)
                        break
            if found_path:
                link = found_path
            else:
                print(f"[DEBUG] skip_stream file not found: {abs_link}")

        stream = _build_stream(link, video=bool(video))
        from pytgcalls.types import GroupCallConfig
        try:
            await asyncio.wait_for(
                assistant.play(
                    chat_id=chat_id, stream=stream, config=GroupCallConfig(auto_start=False),
                ),
                timeout=120,
            )
        except (ConnectionNotFound, TelegramServerError, ConnectionError):
            raise AssistantErr("Telegram server error during skip")

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        extra = {"ffmpeg_parameters": f"-ss {to_seek} -to {duration}"}
        stream = _build_stream(file_path, video=(mode == "video"), extra_params=extra)
        try:
            await assistant.play(chat_id, stream)
        except (ConnectionNotFound, TelegramServerError, ConnectionError):
            raise AssistantErr("Telegram server error during seek")

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        from pytgcalls.types import GroupCallConfig
        stream = MediaStream(
            media_path=link,
            audio_parameters=AudioQuality.HIGH,
            audio_flags=MediaStream.Flags.REQUIRED,
            video_flags=MediaStream.Flags.IGNORE,
        )
        await assistant.play(
            chat_id=config.LOGGER_ID,
            stream=stream,
            config=GroupCallConfig(auto_start=False),
        )
        await asyncio.sleep(0.2)
        await assistant.leave_call(config.LOGGER_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)

        if not link.startswith("http"):
            abs_link = os.path.abspath(link)
            found_path = None
            for ext in ['.mp4', '.webm', '.m4a', '.mkv', '.mp3']:
                test_path = abs_link
                for remove_ext in ['.mp4', '.m4a', '.webm', '.mkv', '.mp3']:
                    test_path = test_path.replace(remove_ext, ext)
                if os.path.exists(test_path):
                    found_path = test_path
                    break
            if not found_path:
                dir_path = os.path.dirname(abs_link)
                base_name = os.path.splitext(os.path.basename(abs_link))[0]
                for f in os.listdir(dir_path) if os.path.exists(dir_path) else []:
                    if f.startswith(base_name):
                        found_path = os.path.join(dir_path, f)
                        break
            if found_path:
                link = found_path
            else:
                raise AssistantErr(f"File not found: {abs_link}")

        stream = _build_stream(link, video=bool(video))
        try:
            from pytgcalls.types import GroupCallConfig
            await asyncio.wait_for(
                assistant.play(
                    chat_id=chat_id, stream=stream, config=GroupCallConfig(auto_start=False),
                ),
                timeout=120,
            )
        except asyncio.TimeoutError:
            raise AssistantErr("Stream initialization timed out (file may be too large)")
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except (ConnectionNotFound, TelegramServerError, ConnectionError):
            raise AssistantErr("Telegram server connection error")
        except Exception as e:
            raise AssistantErr(f"Error: {e}")
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
        except (IndexError, KeyError, TypeError):
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            except Exception:
                return

        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        db[chat_id][0]["played"] = 0
        exis = (check[0]).get("old_dur")
        if exis:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        video = str(streamtype) == "video"

        if "live_" in queued:
            await self._play_live(client, chat_id, original_chat_id, videoid, title, user, check, video, _)
        elif "vid_" in queued:
            await self._play_video(client, chat_id, original_chat_id, videoid, title, user, check, video, _)
        elif "index_" in queued:
            await self._play_index(client, chat_id, original_chat_id, videoid, title, user, check, video, _)
        else:
            await self._play_other(client, chat_id, original_chat_id, videoid, title, user, check, video, queued, streamtype, _)

    async def _play_live(self, client, chat_id, original_chat_id, videoid, title, user, check, video, _):
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await app.send_message(original_chat_id, text=_["call_6"])
        stream = _build_stream(link, video=video)
        try:
            try:
                await client.leave_call(chat_id)
            except Exception:
                pass
            await client.play(chat_id, stream)
        except (NoActiveGroupCall, ConnectionNotFound, TelegramServerError, ConnectionError):
            return await app.send_message(original_chat_id, text=_["call_6"])
        img = await get_thumb(videoid)
        button = stream_markup(_, chat_id)
        run = await app.send_photo(
            chat_id=original_chat_id, photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23], check[0]["dur"], user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"

    async def _play_video(self, client, chat_id, original_chat_id, videoid, title, user, check, video, _):
        mystic = await app.send_message(original_chat_id, _["call_7"])
        try:
            file_path, direct = await YouTube.download(
                videoid, mystic, videoid=True, video=video,
            )
        except Exception:
            return await mystic.edit_text(_["call_6"], disable_web_page_preview=True)
        stream = _build_stream(file_path, video=video)
        try:
            try:
                await client.leave_call(chat_id)
            except Exception:
                pass
            await client.play(chat_id, stream)
        except (NoActiveGroupCall, ConnectionNotFound, TelegramServerError, ConnectionError):
            return await app.send_message(original_chat_id, text=_["call_6"])
        img = await get_thumb(videoid)
        button = stream_markup(_, chat_id)
        await mystic.delete()
        run = await app.send_photo(
            chat_id=original_chat_id, photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23], check[0]["dur"], user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"

    async def _play_index(self, client, chat_id, original_chat_id, videoid, title, user, check, video, _):
        stream = _build_stream(videoid, video=video)
        try:
            try:
                await client.leave_call(chat_id)
            except Exception:
                pass
            await client.play(chat_id, stream)
        except (NoActiveGroupCall, ConnectionNotFound, TelegramServerError, ConnectionError):
            return await app.send_message(original_chat_id, text=_["call_6"])
        button = stream_markup(_, chat_id)
        run = await app.send_photo(
            chat_id=original_chat_id, photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(user),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"

    async def _play_other(self, client, chat_id, original_chat_id, videoid, title, user, check, video, queued, streamtype, _):
        stream = _build_stream(queued, video=video)
        try:
            try:
                await client.leave_call(chat_id)
            except Exception:
                pass
            await client.play(chat_id, stream)
        except (NoActiveGroupCall, ConnectionNotFound, TelegramServerError, ConnectionError):
            return await app.send_message(original_chat_id, text=_["call_6"])
        if videoid == "telegram":
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["markup"] = "tg"
        elif videoid == "soundcloud":
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id, photo=config.SOUNCLOUD_IMG_URL,
                caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["markup"] = "tg"
        else:
            img = await get_thumb(videoid)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id, photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23], check[0]["dur"], user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["markup"] = "stream"
        db[chat_id][0]["mystic"] = run

    async def ping(self):
        pings = [ref.ping for ref in self.clients if ref]
        return str(round(sum(pings) / len(pings), 3)) if pings else "0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        for ref in self.clients:
            if ref:
                await ref.start()

    async def decorators(self):
        async def stream_update_handler(client, update: Update):
            if not isinstance(update, StreamEnded):
                return
            if update.stream_type != StreamEnded.Type.AUDIO:
                return
            try:
                await self.change_stream(client, update.chat_id)
            except Exception:
                await self.stop_stream(update.chat_id)

        for ref in self.clients:
            if ref:
                ref.on_update()(stream_update_handler)


Anony = Call()
