import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import Update
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from pytgcalls.types.stream import StreamEnded

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


class Call(PyTgCalls):
    def __init__(self):
        from ValentinMusic import userbot

        self.one = PyTgCalls(userbot.one) if userbot.one else None
        self.two = PyTgCalls(userbot.two) if userbot.two else None
        self.three = PyTgCalls(userbot.three) if userbot.three else None
        self.four = PyTgCalls(userbot.four) if userbot.four else None
        self.five = PyTgCalls(userbot.five) if userbot.five else None

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
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
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
                if str(speed) == str("0.5"):
                    vs = 2.0
                if str(speed) == str("0.75"):
                    vs = 1.35
                if str(speed) == str("1.5"):
                    vs = 0.68
                if str(speed) == str("2.0"):
                    vs = 0.5
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
        stream = (
            MediaStream(
                media_path=out,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.AUTO_DETECT,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0]["streamtype"] == "video"
            else MediaStream(
                media_path=out,
                audio_parameters=AudioQuality.HIGH,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.play(chat_id, stream)
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
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)

        # Verify file exists and handle extension mismatch
        import os
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
                print(f"[DEBUG] skip_stream file found: {link}")
            else:
                print(f"[DEBUG] skip_stream file not found: {abs_link}")

        if video:
            stream = MediaStream(
                media_path=link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.AUTO_DETECT,
            )
        else:
            stream = MediaStream(
                media_path=link, 
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.IGNORE,
            )
        from pytgcalls.types import GroupCallConfig
        try:
            await assistant.leave_call(chat_id)
        except:
            pass
        await assistant.play(
            chat_id=chat_id,
            stream=stream,
            config=GroupCallConfig(auto_start=False),
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (
            MediaStream(
                media_path=file_path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.AUTO_DETECT,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else MediaStream(
                media_path=file_path,
                audio_parameters=AudioQuality.HIGH,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.IGNORE,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        from pytgcalls.types import GroupCallConfig
        await assistant.play(
            chat_id=config.LOGGER_ID,
            stream=MediaStream(
                media_path=link,
                audio_parameters=AudioQuality.HIGH,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.IGNORE,
            ),
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

        # Verify file exists before attempting to play
        import os
        if not link.startswith("http"):
            # Check if file exists with any extension (yt-dlp may save as webm instead of mp4)
            abs_link = os.path.abspath(link)
            # Check multiple possible extensions
            found_path = None
            for ext in ['.mp4', '.webm', '.m4a', '.mkv', '.mp3']:
                test_path = abs_link
                for remove_ext in ['.mp4', '.m4a', '.webm', '.mkv', '.mp3']:
                    test_path = test_path.replace(remove_ext, ext)
                if os.path.exists(test_path):
                    found_path = test_path
                    break
            if not found_path:
                # Also try to find any file starting with the base name
                dir_path = os.path.dirname(abs_link)
                base_name = os.path.splitext(os.path.basename(abs_link))[0]
                for f in os.listdir(dir_path) if os.path.exists(dir_path) else []:
                    if f.startswith(base_name):
                        found_path = os.path.join(dir_path, f)
                        break
            if found_path:
                link = found_path
                print(f"[DEBUG] File found: {link}")
            else:
                print(f"[DEBUG] File not found: {abs_link}")
                raise AssistantErr(f"File not found: {abs_link}")

        if video:
            stream = MediaStream(
                media_path=link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.AUTO_DETECT,
            )
        else:
            stream = MediaStream(
                media_path=link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=MediaStream.Flags.IGNORE,
            )
        try:
            from pytgcalls.types import GroupCallConfig
            print(f"[DEBUG] Attempting assistant.play for chat {chat_id} with file {link}")

            try:
                await assistant.leave_call(chat_id)
            except Exception:
                pass

            # Now play the stream
            await assistant.play(
                chat_id=chat_id,
                stream=stream,
                config=GroupCallConfig(auto_start=True),
            )
            print(f"[DEBUG] assistant.play successful for chat {chat_id}")
        except NoActiveGroupCall:
            print(f"[DEBUG] join_call failed: NoActiveGroupCall for chat {chat_id}")
            raise AssistantErr(_["call_8"])
        except Exception as e:
            import traceback
            print(f"[DEBUG] join_call failed: {e}")
            traceback.print_exc()
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
        except:
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            except:
                return
        else:
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
            video = True if str(streamtype) == "video" else False
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if video:
                    stream = MediaStream(media_path=link, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.AUTO_DETECT)
                else:
                    stream = MediaStream(media_path=link, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.IGNORE)
                try:
                    try:
                        await client.leave_call(chat_id)
                    except Exception:
                        pass
                    await client.play(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=True if str(streamtype) == "video" else False,
                    )
                except:
                    return await mystic.edit_text(
                        _["call_6"], disable_web_page_preview=True
                    )
                if video:
                    stream = MediaStream(media_path=file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.AUTO_DETECT)
                else:
                    stream = MediaStream(media_path=file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.IGNORE)
                try:
                    try:
                        await client.leave_call(chat_id)
                    except Exception:
                        pass
                    await client.play(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                stream = (
                    MediaStream(media_path=videoid, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.AUTO_DETECT)
                    if str(streamtype) == "video"
                    else MediaStream(media_path=videoid, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.IGNORE)
                )
                try:
                    try:
                        await client.leave_call(chat_id)
                    except Exception:
                        pass
                    await client.play(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                if video:
                    stream = MediaStream(media_path=queued, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.AUTO_DETECT)
                else:
                    stream = MediaStream(media_path=queued, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, audio_flags=MediaStream.Flags.REQUIRED, video_flags=MediaStream.Flags.IGNORE)
                try:
                    try:
                        await client.leave_call(chat_id)
                    except Exception:
                        pass
                    await client.play(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(self.one.ping)
        if config.STRING2:
            pings.append(self.two.ping)
        if config.STRING3:
            pings.append(self.three.ping)
        if config.STRING4:
            pings.append(self.four.ping)
        if config.STRING5:
            pings.append(self.five.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if self.one:
            await self.one.start()
        if self.two:
            await self.two.start()
        if self.three:
            await self.three.start()
        if self.four:
            await self.four.start()
        if self.five:
            await self.five.start()

    async def decorators(self):
        async def stream_update_handler(client, update: Update):
            if not isinstance(update, StreamEnded):
                return
            
            try:
                await self.change_stream(client, update.chat_id)
            except Exception:
                await self.stop_stream(update.chat_id)

        if self.one:
            self.one.on_update()(stream_update_handler)
        if self.two:
            self.two.on_update()(stream_update_handler)
        if self.three:
            self.three.on_update()(stream_update_handler)
        if self.four:
            self.four.on_update()(stream_update_handler)
        if self.five:
            self.five.on_update()(stream_update_handler)


Anony = Call()
