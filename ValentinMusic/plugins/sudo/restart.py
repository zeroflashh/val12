import os
import shutil
import sys

from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS, db
from ValentinMusic.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from ValentinMusic.utils.decorators.language import language
from ValentinMusic.utils.decorators import AdminRightsCheck
from ValentinMusic.core.call import Anony


@app.on_message(filters.command(["logs", "getlog", "getlogs"]) & SUDOERS)
@language
async def log_(client, message, _):
    try:
        await message.reply_document(document="log.txt")
    except Exception:
        await message.reply_text(_["server_1"])


@app.on_message(filters.command(["restart"]) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("Restarting...")
    ac_chats = await get_active_chats()
    for x in ac_chats:
        try:
            await app.send_message(
                chat_id=int(x),
                text=f"{app.mention} is restarting...\n\nYou can start playing again after 15-20 seconds.",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except Exception:
            pass
    try:
        shutil.rmtree("downloads", ignore_errors=True)
        shutil.rmtree("raw_files", ignore_errors=True)
        shutil.rmtree("cache", ignore_errors=True)
    except Exception:
        pass
    await response.edit_text(
        ">> Restart process started, please wait for few seconds until the bot starts..."
    )
    os.execv(sys.executable, [sys.executable, "-m", "ValentinMusic"])


@app.on_message(filters.command(["reboot"]) & filters.group & ~SUDOERS)
@AdminRightsCheck
async def reboot_group_admin(client, message: Message, _, chat_id):
    await reboot_logic(message, _, chat_id)


@app.on_message(filters.command(["reboot"]) & SUDOERS)
@language
async def reboot_sudo(client, message: Message, _):
    chat_id = message.chat.id
    await reboot_logic(message, _, chat_id)


async def reboot_logic(message, _, chat_id):
    m = await message.reply_text(_["reboot_1"].format(message.chat.title))
    
    try:
        # Stop stream and leave VC
        await Anony.stop_stream(chat_id)
    except Exception:
        pass
    
    try:
        # Reset loop
        await set_loop(chat_id, 0)
    except Exception:
        pass
        
    # Clear group cache in db
    if chat_id in db:
        db[chat_id] = []
        
    # Remove from active chats
    await remove_active_chat(chat_id)
    await remove_active_video_chat(chat_id)
    
    await m.edit_text(_["reboot_2"])
