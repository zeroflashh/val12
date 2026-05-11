import asyncio
import aiohttp
import os
import random
import re
import sys
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from ValentinMusic.utils.database import is_on_off
from ValentinMusic.utils.formatters import time_to_seconds


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self.cookie_dir = "ValentinMusic/cookies"
        self.cookies = []
        self.checked = False

    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename for Windows/Linux."""
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list) -> None:
        import aiohttp
        from ValentinMusic.utils.logger import LOGGER
        LOGGER(__name__).info('Saving cookies from urls...')
        async with aiohttp.ClientSession() as session:
            for url in urls:
                name = url.split('/')[-1]
                link = 'https://batbin.me/raw/' + name
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    os.makedirs(self.cookie_dir, exist_ok=True)
                    with open(f'{self.cookie_dir}/{name}.txt', 'wb') as fw:
                        fw.write(await resp.read())
        LOGGER(__name__).info(f'Cookies saved in {self.cookie_dir}.')

    async def search(self, query: str, limit: int = 1):
        results = VideosSearch(query, limit=limit)
        results_json = (await results.next())["result"]
        return results_json

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            channel = result["channel"]["name"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid, channel

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "yt_dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channel = result["channel"]["name"]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
            "channel": channel,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile": self.get_cookies()}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def get_ytdl_formats(self, link: str):
        """Fetch sizes for opus, vp9, and av1 formats."""
        ytdl_opts = {
            "quiet": True,
            "no_warnings": True,
            "cookiefile": self.get_cookies(),
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = info.get("formats", [])
            
            # Find best opus audio
            opus_size = "Unknown"
            for f in formats:
                if f.get("acodec") == "opus" and f.get("vcodec") == "none":
                    if f.get("filesize"):
                        opus_size = self.humanbytes(f["filesize"])
                        break
            
            # Find best vp9 video (prefer 720p or 1080p)
            vp9_size = "Unknown"
            vp9_id = None
            for f in reversed(formats):
                if f.get("vcodec") and "vp9" in f["vcodec"].lower():
                    if f.get("filesize"):
                        vp9_size = self.humanbytes(f["filesize"])
                        vp9_id = f["format_id"]
                        break
            
            # Find best av1 video
            av1_size = "Unknown"
            av1_id = None
            for f in reversed(formats):
                if f.get("vcodec") and "av01" in f["vcodec"].lower():
                    if f.get("filesize"):
                        av1_size = self.humanbytes(f["filesize"])
                        av1_id = f["format_id"]
                        break
                        
        return opus_size, vp9_size, av1_size, vp9_id, av1_id

    @staticmethod
    def humanbytes(size):
        if not size:
            return "Unknown"
        power = 2**10
        n = 0
        Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
        while size > power:
            size /= power
            n += 1
        return f"{round(size, 2)} {Dic_powerN[n]}B"

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if not title:
            title = "Video"
        if videoid:
            link = self.base + link
        print(f"[DEBUG] YouTube.download called for link: {link}")

        # Ensure downloads directory exists
        os.makedirs("downloads", exist_ok=True)

        loop = asyncio.get_running_loop()

        def audio_dl():
            ydl_optssx = {
                "format": "bestaudio[ext=webm][acodec=opus]/bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "cookiefile": self.get_cookies(),
                "extractor_args": {"youtube": ["player_client=android"]},
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            ydl_optssx = {
                "format": "best[height<=?720][width<=?1280][ext=mp4]/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "cookiefile": self.get_cookies(),
                "extractor_args": {"youtube": ["player_client=android"]},
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl(quality="720"):
            title_clean = self.sanitize_filename(title if title else "valentin_download")
            final_title = title_clean.replace(" ", "_")
            fpath = f"downloads/{final_title}"
            print(f"[DEBUG] Starting video download to: {fpath}")
            
            # If format_id is provided, use it. Otherwise use the quality-based format.
            if format_id and format_id not in ["720", "480", "360"]:
                # For specific codecs, we might need to merge with audio
                actual_format = f"{format_id}+bestaudio/best"
            else:
                q = format_id if format_id else quality
                actual_format = f"(bestvideo[height<={q}][ext=mp4])+(bestaudio[ext=m4a])/best[height<={q}]"

            ydl_optssx = {
                "format": actual_format,
                "outtmpl": fpath + ".%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
                "cookiefile": self.get_cookies(),
                "extractor_args": {"youtube": ["player_client=android"]},
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, download=True)
            ext = info.get('ext', 'mp4')
            # Find the actual file on disk
            for file in os.listdir("downloads"):
                if file.startswith(final_title) and file.endswith(ext):
                    return os.path.join("downloads", file)
            # Fallback
            return f"downloads/{final_title}.{ext}"

        def song_audio_dl():
            title_clean = self.sanitize_filename(title if title else "valentin_download")
            final_title = title_clean.replace(" ", "_")
            fpath = f"downloads/{final_title}.%(ext)s"
            print(f"[DEBUG] Starting audio download to: {fpath}")
            # Use specific opus format if format_id is 'opus'
            actual_format = "bestaudio[acodec=opus]/bestaudio/best" if format_id == "opus" else (format_id if format_id else "bestaudio/best")
            
            ydl_optssx = {
                "format": actual_format,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "cookiefile": self.get_cookies(),
                "extractor_args": {"youtube": ["player_client=android"]},
            }
            # Only apply mp3 postprocessing if it's not a direct opus/other request
            if actual_format == "bestaudio/best" or not format_id:
                ydl_optssx["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
                ext = "mp3"
            else:
                ext = "opus" if "opus" in actual_format else "m4a"

            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, download=True)
            # Find the actual file on disk
            for file in os.listdir("downloads"):
                if file.startswith(final_title) and file.endswith(ext):
                    return os.path.join("downloads", file)
            # Fallback
            return f"downloads/{final_title}.{ext}"

        def direct_stream_url(is_video):
            ydl_opts = {
                "format": "best[height<=?720][width<=?1280][ext=mp4]/best" if is_video else "bestaudio[ext=webm][acodec=opus]/bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "cookiefile": self.get_cookies(),
                "extractor_args": {"youtube": ["player_client=android"]},
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    if info and "url" in info:
                        return info["url"]
                    elif info and "requested_formats" in info:
                        return info["requested_formats"][0]["url"]
            except Exception as e:
                print(f"[DEBUG] direct_stream_url yt-dlp exception: {e}")
            return None

        if songvideo:
            quality = format_id if format_id else "720"
            downloaded_file = await loop.run_in_executor(None, song_video_dl, quality)
            return downloaded_file, True
        elif songaudio:
            downloaded_file = await loop.run_in_executor(None, song_audio_dl)
            return downloaded_file, True
        elif video:
            if await is_on_off(1):
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
            else:
                downloaded_file = await loop.run_in_executor(None, direct_stream_url, True)
                direct = None
                if not downloaded_file:
                    raise Exception("Failed to fetch stream URL")
        else:
            if await is_on_off(1):
                direct = True
                downloaded_file = await loop.run_in_executor(None, audio_dl)
            else:
                downloaded_file = await loop.run_in_executor(None, direct_stream_url, False)
                direct = None
                if not downloaded_file:
                    raise Exception("Failed to fetch stream URL")
        print(f"[DEBUG] YouTube.download returning: {downloaded_file}, direct={direct}")
        return downloaded_file, direct
