from typing import Union

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message

from ValentinMusic import app
from ValentinMusic.utils import help_pannel
from ValentinMusic.utils.database import get_lang
from ValentinMusic.utils.decorators.language import LanguageStart, languageCB
from ValentinMusic.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("help_back") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except Exception:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        if update.message.photo:
            await update.message.delete()
            await client.send_message(
                chat_id=chat_id,
                text=_["help_1"].format(SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        else:
            await update.edit_message_text(
                _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard
            )
    else:
        try:
            await update.delete()
        except Exception:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, query, _):
    callback_data = query.data.strip()
    try:
        cb = callback_data.split(None, 1)[1]
    except IndexError:
        return await query.answer("Invalid callback data.", show_alert=True)
        
    print(f"[DEBUG] Help callback triggered: {cb}")
    keyboard = help_back_markup(_)
    
    if cb == "hb1":
        text = _["HELP_1"]
    elif cb == "hb2":
        text = _["HELP_2"]
    elif cb == "hb3":
        text = _["HELP_3"]
    elif cb == "hb4":
        from ValentinMusic.misc import SUDOERS
        if query.from_user.id not in SUDOERS:
            return await query.answer(_["sudo_help_err"], show_alert=True)
        text = _["HELP_4"]

    if not text:
        return await query.answer("No help text found for this category.", show_alert=True)

    try:
        if query.message.photo:
            await query.message.delete()
            await client.send_message(
                chat_id=query.message.chat.id,
                text=text,
                reply_markup=keyboard
            )
        else:
            await query.edit_message_text(text, reply_markup=keyboard)
    except Exception as e:
        import traceback
        print(f"[ERROR] Help callback {cb} failed:")
        traceback.print_exc()
        await query.answer(f"Error: {str(e)[:50]}", show_alert=True)
