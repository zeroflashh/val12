import os

from gtts import gTTS
from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from config import BANNED_USERS


@app.on_message(filters.command(["tts", "speak"]) & ~BANNED_USERS)
async def tts_cmd(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<b>Usage:</b> /tts [text] or reply to a message.\n<b>Example:</b> /tts Hello world!"
        )

    if len(message.command) >= 2:
        text = message.text.split(None, 1)[1].strip()
    else:
        text = message.reply_to_message.text or message.reply_to_message.caption

    if not text:
        return await message.reply_text("<b>Please provide text to convert.</b>")

    m = await message.reply_text("🔊 <b>Converting to speech...</b>")

    try:
        # User specified language or default to en
        # We can extract language if it's the first word after /tts like /tts hi Hello
        # But for now let's stick to en as requested or simple logic
        tts = gTTS(text=text, lang="en", slow=False)
        
        # Use a unique filename to avoid collisions
        tts_file = f"downloads/tts_{message.from_user.id}_{message.id}.mp3"
        os.makedirs("downloads", exist_ok=True)
        tts.save(tts_file)

        # Reply to the command sender (message)
        await message.reply_voice(voice=tts_file)

        # Clean up
        if os.path.exists(tts_file):
            os.remove(tts_file)
        try:
            await m.delete()
        except:
            pass
    except Exception as e:
        try:
            await m.edit(f"❌ <b>TTS conversion failed:</b> {str(e)}")
        except:
            pass
