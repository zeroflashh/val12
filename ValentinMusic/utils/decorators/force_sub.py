from pyrogram import enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import SUPPORT_CHANNEL
from ValentinMusic import app
from strings import get_string
from ValentinMusic.utils.database import get_lang

def check_force_sub(func):
    async def wrapper(client, message: Message, *args, **kwargs):
        if not SUPPORT_CHANNEL:
            return await func(client, message, *args, **kwargs)

        try:
            # Extract channel username from link
            channel = SUPPORT_CHANNEL.split("/")[-1]
            await client.get_chat_member(channel, message.from_user.id)
        except UserNotParticipant:
            chat_id = message.chat.id
            language = await get_lang(chat_id)
            _ = get_string(language)
            
            # Use keys from language file if available, otherwise fallback
            btn_text = _["S_B_9"] if "S_B_9" in _ else "Join Channel"
            text = _["force_sub_text"] if "force_sub_text" in _ else "To use this bot, you must join our support channel first!"
            
            buttons = [
                [
                    InlineKeyboardButton(
                        text=btn_text,
                        url=SUPPORT_CHANNEL,
                    )
                ]
            ]
            return await message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except Exception:
            pass
            
        return await func(client, message, *args, **kwargs)
    return wrapper
