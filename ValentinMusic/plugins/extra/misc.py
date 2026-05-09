import secrets
import string

import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import Carbon, app

RUNS_LIST = [
    "Where do you think you're going?",
    "Huh? what? did they get away?",
    "ZZzzZZzz... Huh? what? oh, just them again, never mind.",
    "Get back here!",
    "Not so fast...",
    "Look out for the wall!",
    "Don't leave me alone with them!!",
    "You run, you die.",
    "Jokes on you, I'm everywhere",
    "You're gonna regret that...",
    "See /dice.",
    "Xavier would have done it better.",
    "You clearly haven't seen what happened to the last person who ran.",
    "Nothing unexpected to me.",
    "Run Forrest run!",
    "I bet you can't even run in real life...",
    "Physics says otherwise.",
    "My bot told me to run but I'm lazy.",
    "404: Dignity not found.",
    "You can run, but you can't hide!",
]


@app.on_message(filters.command("commit"))
async def commit(_, message: Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://whatthecommit.com/index.txt") as resp:
                text = await resp.text()
        await message.reply_text(f"🔧 <code>{text.strip()}</code>")
    except Exception:
        await message.reply_text("❌ Failed to fetch commit message.")


@app.on_message(filters.command("RTFM", "#"))
async def rtfm(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message!")
    await message.delete()
    await message.reply_to_message.reply_text(
        "📖 <b>READ THE DOCS!</b>\n\n<i>Your answer is probably in there.</i>"
    )


@app.on_message(filters.command("runs"))
async def runs(_, message: Message):
    import random
    await message.reply_text(random.choice(RUNS_LIST))


@app.on_message(filters.command("id"))
async def getid(client, message: Message):
    chat = message.chat
    your_id = message.from_user.id if message.from_user else 0
    message_id = message.id

    text = f"<b>💬 Message ID:</b> <code>{message_id}</code>\n"
    text += f"<b>👤 Your ID:</b> <code>{your_id}</code>\n"

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user = await client.get_users(split)
            text += f"<b>🔎 User ID:</b> <code>{user.id}</code>\n"
        except Exception:
            pass

    text += f"<b>💬 Chat ID:</b> <code>{chat.id}</code>\n"

    reply = message.reply_to_message
    if reply and reply.from_user:
        text += f"\n<b>↩️ Replied User ID:</b> <code>{reply.from_user.id}</code>"
    elif reply and reply.sender_chat:
        text += f"\n<b>↩️ Replied Chat ID:</b> <code>{reply.sender_chat.id}</code>"

    await message.reply_text(text, disable_web_page_preview=True)


@app.on_message(filters.command("random"))
async def random_pass(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "<b>Usage:</b> /random [length]\n<b>Example:</b> /random 16"
        )
    try:
        length = int(message.text.split(None, 1)[1])
        if 1 < length < 1000:
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = "".join(secrets.choice(alphabet) for _ in range(length))
            await message.reply_text(
                f"🔐 <b>Generated Password:</b>\n<code>{password}</code>"
            )
        else:
            await message.reply_text("Length must be between 2 and 999.")
    except ValueError:
        await message.reply_text("Please pass a valid number.")


@app.on_message(filters.command("tr"))
async def translate(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Usage:</b> /tr [lang_code]\nReply to a message to translate it.\n<b>Example:</b> /tr en"
        )
    lang = message.text.split(None, 1)[1].strip()
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("Reply to a text message to translate it.")
    text = reply.text or reply.caption
    if not text:
        return await message.reply_text("Reply to a text message to translate it.")

    # Get language name for display
    lang_names = {
        "en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
        "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian",
        "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "ar": "Arabic",
        "gu": "Gujarati", "pa": "Punjabi", "bn": "Bengali",
        "ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "kn": "Kannada",
        "id": "Indonesian", "si": "Sinhala", "bho": "Bhojpuri",
    }
    lang_name = lang_names.get(lang.lower(), lang.upper())

    from ValentinMusic.utils.database import get_lang
    from strings import get_string
    language = await get_lang(message.chat.id)
    _ = get_string(language)

    try:
        m = await message.reply_text(_["tr_1"].format(lang_name))
        async with aiohttp.ClientSession() as session:
            url = f"https://api.mymemory.translated.net/get?q={text[:500]}&langpair=autodetect|{lang}"
            async with session.get(url) as resp:
                data = await resp.json()
                translated = data["responseData"]["translatedText"]

        await m.edit_text(_["tr_2"].format(lang_name))
        await message.reply_text(_["tr_3"].format(translated))
        if message.from_user:
            try:
                await message.delete()
            except:
                pass
    except Exception as e:
        await message.reply_text(f"❌ Translation failed: {str(e)}")


@app.on_message(filters.command("carbon"))
async def carbon_cmd(_, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.text:
        return await message.reply_text(
            "<b>Reply to a text message</b> to generate a carbon image."
        )
    m = await message.reply_text("🎨 <b>Generating carbon...</b>")
    try:
        carbon_img = await Carbon.generate(reply.text, reply.id)
        await message.reply_photo(carbon_img)
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Carbon generation failed: {str(e)}")