"""
Ban Ghosts Module — Remove deleted/deactivated accounts from a group.
Invite Module — Generate group invite links.
"""
from pyrogram import filters, enums
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS


@app.on_message(filters.command("ban_ghosts") & filters.group)
async def ban_ghosts(client, message: Message):
    # Check if user is admin
    if not message.from_user:
        return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        if message.from_user.id not in SUDOERS:
            return await message.reply_text("⛔ You need admin privileges for this.")

    m = await message.reply_text("👻 <b>Scanning for ghost accounts...</b>")

    deleted_count = 0
    failed_count = 0

    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            try:
                await client.ban_chat_member(message.chat.id, member.user.id)
                await client.unban_chat_member(message.chat.id, member.user.id)
                deleted_count += 1
            except Exception:
                failed_count += 1

    text = (
        f"👻 <b>Ghost Cleanup Complete!</b>\n\n"
        f"<b>Removed:</b> {deleted_count}\n"
        f"<b>Failed:</b> {failed_count}"
    )
    await m.edit(text)


@app.on_message(filters.command("invite") & filters.group)
async def invite_link(client, message: Message):
    # Check if user is admin
    if not message.from_user:
        return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        if message.from_user.id not in SUDOERS:
            return await message.reply_text("⛔ You need admin privileges for this.")

    try:
        link = await client.export_chat_invite_link(message.chat.id)
        await message.reply_text(
            f"🔗 <b>Invite Link:</b>\n{link}",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to generate invite link.\n{str(e)}")
