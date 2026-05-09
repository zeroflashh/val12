from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ValentinMusic import app, YouTube
from ValentinMusic.utils.database import get_lang
from config import BANNED_USERS
from strings import get_string


@app.on_message(filters.command(["search"]) & ~BANNED_USERS)
async def yt_search(client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("<b>Usage:</b> /search [song name]")
        
        query = message.text.split(None, 1)[1]
        chat_id = message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        
        m = await message.reply_text(_["search_1"])
        
        results = await YouTube.search(query, limit=10)
        if not results:
            return await m.edit_text("❌ No results found.")
        
        # Display first 5 results
        text = _["search_2"].format(query) + "\n\n"
        row = []
        
        for i, result in enumerate(results[:5], 1):
            title = result["title"]
            duration = result["duration"]
            channel = result["channel"]["name"]
            link = result["link"]
            text += _["search_3"].format(i, link, title, duration, channel)
            row.append(InlineKeyboardButton(text=str(i), callback_data=f"search_play|{result['id']}"))

        # Next button
        next_button = [InlineKeyboardButton(text="Next ➡️", callback_data=f"search_next|1|{query[:20]}")]
        
        markup = InlineKeyboardMarkup([row, next_button])
        
        await m.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_callback_query(filters.regex(r"^search_next\|") & ~BANNED_USERS)
async def search_pagination(client, CallbackQuery):
    try:
        data = CallbackQuery.data.split("|")
        page = int(data[1])
        query = data[2]
        
        chat_id = CallbackQuery.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        
        results = await YouTube.search(query, limit=10)
        if not results:
            return await CallbackQuery.answer("No more results.", show_alert=True)
        
        if page == 0: # First page
            display_results = results[:5]
            start_index = 1
            next_page = 1
            btn_text = "Next ➡️"
        else: # Second page
            display_results = results[5:10]
            start_index = 6
            next_page = 0
            btn_text = "⬅️ Previous"
            
        text = _["search_2"].format(query) + "\n\n"
        row = []
        for i, result in enumerate(display_results, start_index):
            title = result["title"]
            duration = result["duration"]
            channel = result["channel"]["name"]
            link = result["link"]
            text += _["search_3"].format(i, link, title, duration, channel)
            row.append(InlineKeyboardButton(text=str(i), callback_data=f"search_play|{result['id']}"))
            
        nav_button = [InlineKeyboardButton(text=btn_text, callback_data=f"search_next|{next_page}|{query}")]
        markup = InlineKeyboardMarkup([row, nav_button])
        
        await CallbackQuery.edit_message_text(text, reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        await CallbackQuery.answer(f"Error: {e}", show_alert=True)


@app.on_callback_query(filters.regex(r"^search_play\|") & ~BANNED_USERS)
async def search_play_callback(client, CallbackQuery):
    try:
        video_id = CallbackQuery.data.split("|")[1]
        chat_id = CallbackQuery.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        
        await CallbackQuery.answer(_["search_3"].split("\n")[0], show_alert=True) # Just the first line for toast
        
        from ValentinMusic.plugins.play.play import play_commnd
        
        # Modify the message to act as a /play command from the user who clicked
        msg = CallbackQuery.message
        msg.from_user = CallbackQuery.from_user
        url = f"https://www.youtube.com/watch?v={video_id}"
        msg.text = f"/play {url}"
        msg.command = ["play", url]
        
        # We don't delete it here because PlayWrapper will try to delete it
        # But wait, CallbackQuery.message is the search result message.
        # If PlayWrapper deletes it, the search UI is gone. That's good.
        
        await play_commnd(client, msg)
        await CallbackQuery.message.delete() # Ensure search UI is gone if PlayWrapper failed to delete
    except Exception as e:
        try:
            await CallbackQuery.answer(f"Error: {e}", show_alert=True)
        except:
            pass
