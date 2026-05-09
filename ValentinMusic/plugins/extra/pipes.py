"""
Pipes Module — Forward messages between chats (sudo only, in-memory).
Ported from WilliamButcherBot (MIT License) by TheHamkerCat.
"""
from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS

pipes_list = {}


@app.on_message(~filters.me & filters.group, group=500)
async def pipes_worker(_, message: Message):
    chat_id = message.chat.id
    if chat_id in pipes_list:
        try:
            await message.forward(pipes_list[chat_id])
        except Exception:
            pass


@app.on_message(filters.command("activate_pipe") & SUDOERS)
async def activate_pipe_func(_, message: Message):
    if len(message.command) != 3:
        return await message.reply(
            "<b>Usage:</b>\n/activate_pipe [FROM_CHAT_ID] [TO_CHAT_ID]"
        )
    text = message.text.strip().split()
    try:
        from_chat = int(text[1])
        to_chat = int(text[2])
    except ValueError:
        return await message.reply("Chat IDs must be integers.")

    if from_chat in pipes_list:
        return await message.reply_text("⚠️ This pipe is already active.")

    pipes_list[from_chat] = to_chat
    await message.reply_text(
        f"✅ <b>Pipe activated!</b>\n"
        f"<b>From:</b> <code>{from_chat}</code>\n"
        f"<b>To:</b> <code>{to_chat}</code>"
    )


@app.on_message(filters.command("deactivate_pipe") & SUDOERS)
async def deactivate_pipe_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "<b>Usage:</b>\n/deactivate_pipe [FROM_CHAT_ID]"
        )
    try:
        from_chat = int(message.text.strip().split()[1])
    except ValueError:
        return await message.reply("Chat ID must be an integer.")

    if from_chat not in pipes_list:
        return await message.reply_text("⚠️ This pipe is not active.")

    del pipes_list[from_chat]
    await message.reply_text("✅ <b>Pipe deactivated.</b>")


@app.on_message(filters.command("pipes") & SUDOERS)
async def show_pipes_func(_, message: Message):
    if not pipes_list:
        return await message.reply_text("No active pipes.")
    text = "<b>🔗 Active Pipes:</b>\n\n"
    for count, (from_c, to_c) in enumerate(pipes_list.items(), 1):
        text += (
            f"<b>Pipe #{count}</b>\n"
            f"  <b>From:</b> <code>{from_c}</code>\n"
            f"  <b>To:</b> <code>{to_c}</code>\n\n"
        )
    await message.reply_text(text)
