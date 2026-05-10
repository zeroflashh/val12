import asyncio
import pyrogram
import telethon
from pyrogram import Client, filters, errors
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError,
    PasswordHashInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
)

from ValentinMusic import app
from ValentinMusic.utils.database import get_lang
from strings import get_string
import config

GEN_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Pyrogram", callback_data="gen_pyro"),
            InlineKeyboardButton("Telethon", callback_data="gen_tele"),
        ],
        [
            InlineKeyboardButton("Close", callback_data="close"),
        ]
    ]
)


@app.on_message(filters.command(["genstr", "generate"]) & filters.private)
async def generate_session_msg(client, message: Message):
    await message.reply_text(
        "<b>>> String Session Generator</b>\n\n"
        "Choose the library for which you want to generate a string session.\n\n"
        "<b>Pyrogram</b> — For main bot / assistant accounts (music player)\n"
        "<b>Telethon</b> — For userbot / inline bots\n\n"
        "Use <code>/cancel</code> to abort anytime.",
        reply_markup=GEN_BUTTONS
    )


@app.on_callback_query(filters.regex(r"^gen_(pyro|tele)"))
async def gen_callback(client, callback_query):
    lib = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    language = await get_lang(callback_query.message.chat.id)
    _ = get_string(language)

    await callback_query.message.delete()

    msg = await client.send_message(
        user_id,
        f"<b>>> String Session — {lib.upper()}</b>\n\n"
        "Send your phone number with country code.\n"
        "Example: <code>+911234567890</code>\n\n"
        "Send /cancel to abort."
    )

    try:
        phone_number_msg = await client.listen(user_id, timeout=120)
        if phone_number_msg.text == "/cancel":
            return await msg.edit(_["session_1"].format("Cancelled", "N/A"))

        phone_number = phone_number_msg.text
        await msg.delete()

        m = await client.send_message(user_id, "<b>>> Processing...</b>")

        if lib == "pyro":
            session_str, version = await generate_pyrogram_session(
                client, user_id, phone_number, m, _
            )
        else:
            session_str, version = await generate_telethon_session(
                client, user_id, phone_number, m, _
            )

        await client.send_message(
            user_id,
            f"<b>>> String Session Generated</b>\n\n"
            f"Library: <code>{version}</code>\n"
            f"Length: <code>{len(session_str)}</code> chars\n\n"
            f"<code>{session_str}</code>\n\n"
            "⚠️ <b>Keep this session string safe!</b>\n"
            "Anyone with this string can access your account.\n\n"
            "<b>How to use:</b>\n"
            "• Add to .env file as <code>STRING_SESSION</code> (Pyrogram)\n"
            "• Or <code>STRING_SESSION2</code>, <code>STRING_SESSION3</code>, etc.\n"
            "• Rebuild and restart the bot.\n\n"
            "⚠️ <b>Never share this string with anyone.</b>",
        )
        await m.delete()

    except asyncio.TimeoutError:
        await msg.edit(_["session_1"].format("Timed out (2 min)", version if "version" in dir() else "N/A"))
    except Exception as e:
        await msg.edit(f"<b>Error:</b> <code>{str(e)}</code>")


async def generate_pyrogram_session(bot, user_id, phone_number, m, _):
    temp_client = Client(
        name="temp_pyro",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        in_memory=True
    )

    await temp_client.connect()
    version = f"Pyrogram {pyrogram.__version__}"

    try:
        code_hash = await temp_client.send_code(phone_number)
        await m.edit(
            "<b>>> OTP Sent</b>\n\n"
            "Enter the OTP code from Telegram.\n"
            "Format: <code>12345</code> (no spaces)\n\n"
            "Send /cancel to abort."
        )

        otp_msg = await bot.listen(user_id, timeout=120)
        if otp_msg.text == "/cancel":
            raise asyncio.CancelledError()

        otp = otp_msg.text.replace(" ", "")

        try:
            await temp_client.sign_in(phone_number, code_hash.phone_code_hash, otp)
        except errors.SessionPasswordNeeded:
            await m.edit("<b>>> 2FA Required</b>\n\nEnter your Two-Step Verification password.\nSend /cancel to abort.")
            pwd_msg = await bot.listen(user_id, timeout=120)
            if pwd_msg.text == "/cancel":
                raise asyncio.CancelledError()
            password = pwd_msg.text
            await temp_client.check_password(password)
            await temp_client.sign_in(phone_number, code_hash.phone_code_hash, otp)

        session_string = await temp_client.export_session_string()
        await m.delete()
        return session_string, version

    except asyncio.CancelledError:
        await m.edit(_["session_1"].format("User cancelled", version))
        raise
    except Exception as e:
        await m.edit(_["session_1"].format(str(e), version))
        raise
    finally:
        await temp_client.disconnect()


async def generate_telethon_session(bot, user_id, phone_number, m, _):
    temp_client = TelegramClient(
        StringSession(),
        config.API_ID,
        config.API_HASH,
    )
    await temp_client.connect()
    version = f"Telethon {telethon.__version__}"

    try:
        send_code = await temp_client.send_code_request(phone_number)
        await m.edit(
            "<b>>> OTP Sent</b>\n\n"
            "Enter the OTP code from Telegram.\n"
            "Format: <code>12345</code> (no spaces)\n\n"
            "Send /cancel to abort."
        )

        otp_msg = await bot.listen(user_id, timeout=120)
        if otp_msg.text == "/cancel":
            raise asyncio.CancelledError()

        otp = otp_msg.text.replace(" ", "")

        try:
            await temp_client.sign_in(phone_number, otp, password=None)
        except SessionPasswordNeededError:
            await m.edit("<b>>> 2FA Required</b>\n\nEnter your Two-Step Verification password.\nSend /cancel to abort.")
            pwd_msg = await bot.listen(user_id, timeout=120)
            if pwd_msg.text == "/cancel":
                raise asyncio.CancelledError()
            password = pwd_msg.text
            await temp_client.sign_in(password=password)

        session_string = temp_client.session.save()
        await m.delete()
        return session_string, version

    except asyncio.CancelledError:
        await m.edit(_["session_1"].format("User cancelled", version))
        raise
    except Exception as e:
        await m.edit(_["session_1"].format(str(e), version))
        raise
    finally:
        await temp_client.disconnect()
