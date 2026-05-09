from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType, ChatMembersFilter
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.utils.database import get_lang
from strings import get_string
from config import BANNED_USERS

@app.on_message(filters.command(["adminlist", "admins", "admin_list"]) & ~BANNED_USERS)
async def adminlist(client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(">> This command only works in groups.")
    
    chat_id = message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)

    try:
        administrators = []
        async for m in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            administrators.append(m)
        
        if not administrators:
            return await message.reply_text(_["AL_4"])

        # Sort: Owner first, then others by name
        administrators.sort(key=lambda x: (x.status != ChatMemberStatus.OWNER, x.user.first_name if x.user and x.user.first_name else ""))
        
        text = _["AL_1"].format(message.chat.title) + "\n\n"
        
        owner = next((a for a in administrators if a.status == ChatMemberStatus.OWNER), None)
        admins = [a for a in administrators if a.status != ChatMemberStatus.OWNER]
        
        if owner and owner.user:
            custom_title = f" ({owner.custom_title})" if owner.custom_title else ""
            text += _["AL_2"].format(owner.user.mention, custom_title) + "\n\n"
        
        if admins:
            text += _["AL_3"] + "\n"
            for i, admin in enumerate(admins, 1):
                if not admin.user:
                    continue
                user_link = admin.user.mention
                custom_title = f" ({admin.custom_title})" if admin.custom_title else ""
                text += f"<b>{i}.</b> {user_link}{custom_title}\n"
        
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f">> Error: {str(e)}")
