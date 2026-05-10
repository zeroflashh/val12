from strings import get_string

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS
from config import SUPPORT_CHAT
from ValentinMusic.utils.database import get_lang, is_maintenance


def language(mystic):
    async def wrapper(client, message, **kwargs):
        if await is_maintenance() is True:
            if message.from_user and message.from_user.id not in SUDOERS.user_ids:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )
        try:
            await message.delete()
        except:
            pass

        try:
            language = await get_lang(message.chat.id)
            strings = get_string(language)
        except:
            strings = get_string("en")
        return await mystic(client, message, strings)

    return wrapper


def languageCB(mystic):
    async def wrapper(client, CallbackQuery, **kwargs):
        if await is_maintenance() is True:
            if CallbackQuery.from_user and CallbackQuery.from_user.id not in SUDOERS.user_ids:
                 return await CallbackQuery.answer(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    show_alert=True,
                )
        try:
            language = await get_lang(CallbackQuery.message.chat.id)
            strings = get_string(language)
        except:
            strings = get_string("en")
        return await mystic(client, CallbackQuery, strings)

    return wrapper


def LanguageStart(mystic):
    async def wrapper(client, message, **kwargs):
        try:
            language = await get_lang(message.chat.id)
            strings = get_string(language)
        except:
            strings = get_string("en")
        return await mystic(client, message, strings)

    return wrapper
