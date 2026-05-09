from pyrogram import filters
from pyrogram.types import Message
from unidecode import unidecode

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS
from ValentinMusic.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)


@app.on_message(filters.command(["activevc"]) & SUDOERS)
async def activevc(_, message: Message):
    """
    Combined command for active voice/video chats.
    Shows total counts and lists all active chats with names.
    Public chats shown as hyperlinks, private chats shown by category.
    """
    mystic = await message.reply_text("» ɢᴇᴛᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ʟɪsᴛ...")

    # Get both voice and video chats
    served_chats = await get_active_chats()
    served_video_chats = await get_active_video_chats()

    # Build voice chat list
    voice_text = ""
    voice_count = 0
    for x in served_chats:
        try:
            title = (await app.get_chat(x)).title
        except:
            await remove_active_chat(x)
            continue
        try:
            if (await app.get_chat(x)).username:
                user = (await app.get_chat(x)).username
                voice_text += f"<b>{voice_count + 1}.</b> <a href=https://t.me/{user}>{unidecode(title).upper()}</a> [<code>{x}</code>]\n"
            else:
                voice_text += (
                    f"<b>{voice_count + 1}.</b> {unidecode(title).upper()} [<code>{x}</code>]\n"
                )
            voice_count += 1
        except:
            continue

    # Build video chat list
    video_text = ""
    video_count = 0
    for x in served_video_chats:
        try:
            title = (await app.get_chat(x)).title
        except:
            await remove_active_video_chat(x)
            continue
        try:
            if (await app.get_chat(x)).username:
                user = (await app.get_chat(x)).username
                video_text += f"<b>{video_count + 1}.</b> <a href=https://t.me/{user}>{unidecode(title).upper()}</a> [<code>{x}</code>]\n"
            else:
                video_text += (
                    f"<b>{video_count + 1}.</b> {unidecode(title).upper()} [<code>{x}</code>]\n"
                )
            video_count += 1
        except:
            continue

    # Build final response with counts and lists
    total_count = voice_count + video_count

    response = f"✨ <b><u>ᴀᴄᴛɪᴠᴇ ᴄᴀʟʟs sᴛᴀᴛs</u></b>\n\n"
    response += f"<b>🎙️ ᴠᴏɪᴄᴇ:</b> {voice_count}\n"
    response += f"<b>📹 ᴠɪᴅᴇᴏ:</b> {video_count}\n"
    response += f"<b>📈 ᴛᴏᴛᴀʟ:</b> {total_count}\n\n"

    if voice_text:
        response += f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs :</b>\n\n{voice_text}\n"

    if video_text:
        response += f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs :</b>\n\n{video_text}"

    if not voice_text and not video_text:
        response += f"» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄʜᴀᴛs ᴏɴ {app.mention}."

    await mystic.edit_text(
        response,
        disable_web_page_preview=True,
    )
