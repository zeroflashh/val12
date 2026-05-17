import os
import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.utils.database import get_lang
from strings import get_string
from config import BANNED_USERS


async def fetch_lyrics(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception:
        return None


@app.on_message(filters.command(["lyrics", "lyric"]) & ~BANNED_USERS)
async def lyrics_search(client, message: Message):
    chat_id = message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    
    if len(message.command) < 2:
        return await message.reply_text(
            _["lyric_1"] if "lyric_1" in _ else "<b>Usage:</b> /lyrics [song name]"
        )
    
    query = message.text.split(None, 1)[1]
    query = query.replace("lyrics", "").replace("Lyrics", "").strip()
    
    m = await message.reply_text(
        _["lyric_2"] if "lyric_2" in _ else "<b>Searching for lyrics...</b>"
    )
    
    sources = [
        {"name": "LRCLIB", "url": f"https://lrclib.net/api/search?q={query}"},
        {"name": "Genius", "url": f"https://some-random-api.com/lyrics?title={query}"},
    ]
    
    async with aiohttp.ClientSession() as session:
        for source in sources:
            await m.edit(
                _["lyric_3"].format(source["name"]) if "lyric_3" in _ else f"<b>Searching via {source['name']}...</b>"
            )
            data = await fetch_lyrics(session, source["url"])
            
            if not data:
                continue

            lyrics = None
            title = query
            artist = ""

            if source["name"] == "LRCLIB":
                if isinstance(data, list) and len(data) > 0:
                    lyrics = data[0].get("plainLyrics") or data[0].get("lyrics")
                    title = data[0].get("trackName", query)
                    artist = data[0].get("artistName", "")
            elif isinstance(data, dict):
                lyrics = data.get("lyrics")
                if not lyrics:
                    lyrics = data.get("text")
                title = data.get("title", query)
                artist = data.get("artist") or data.get("author", "")
                
            if lyrics:
                header = f"<b>Lyrics for: {title}</b>"
                if artist:
                    header = f"<b>Lyrics for: {title} ({artist})</b>"
                
                text = f"{header}\n\n{lyrics}\n\n<b>Source:</b> {source['name']}"
                
                if len(text) > 4096:
                    path = f"downloads/lyrics_{message.from_user.id}.txt"
                    os.makedirs("downloads", exist_ok=True)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text)
                    await message.reply_document(path, caption=header)
                    if os.path.exists(path):
                        os.remove(path)
                    await m.delete()
                else:
                    await m.edit(text)
                return

    await m.edit(_["lyric_4"] if "lyric_4" in _ else "<b>No lyrics found.</b>")
