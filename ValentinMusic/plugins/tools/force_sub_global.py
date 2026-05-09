from pyrogram import filters, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import SUPPORT_CHANNEL, BANNED_USERS
from ValentinMusic import app
from strings import get_string
from ValentinMusic.utils.database import get_lang


# Force Subscription check for private chats removed to ensure professional user experience.



SUPPORTED_COMMANDS = {
    "start", "help", "settings", "play", "vplay", "song", "ping", "stats",
    "skip", "pause", "resume", "stop", "end", "shuffle", "loop", "queue",
    "cplay", "cvplay", "cstart", "reload", "admin", "auth", "unauth",
    "blacklist", "unblacklist", "broadcast", "mcast", "sudolist",
    "speedtest", "sysstats", "lyrics", "search", "video", "reboot", "update",
    "language", "ytdl", "adminlist",
    # WBB ported modules
    "dice", "dart", "basketball", "bowling", "slots", "football",
    "info", "chat_info", "karma", "karma_toggle",
    "commit", "runs", "id", "random", "tr", "carbon",
    "activate_pipe", "deactivate_pipe", "pipes",
    "q", "ship", "couple",
    "kang", "sticker_id", "get_sticker",
    "ban_ghosts", "invite",
}

@app.on_message(filters.group & ~BANNED_USERS, group=-1)
async def force_sub_group(client, message: Message):
    if not SUPPORT_CHANNEL:
        return
    
    if not message.from_user:
        return
    
    if not message.text or not message.text.startswith(("/", "!")):
        return

    # Extract the command name
    parts = message.text.split(None, 1)[0][1:].split("@")
    cmd = parts[0].lower()
    bot_username = parts[1].lower() if len(parts) > 1 else None
    print(f"[DEBUG] Force Sub checking command: {cmd} (bot: {bot_username})")

    # Rule 1: If command has a bot username, only trigger if it's OUR username
    if bot_username:
        if not app.username or bot_username != app.username.lower():
            return

    # Rule 2: If no bot username, only trigger if it's a command we support
    if not bot_username and cmd not in SUPPORTED_COMMANDS:
        return

    try:
        channel = SUPPORT_CHANNEL.split("/")[-1]
        await client.get_chat_member(channel, message.from_user.id)
    except UserNotParticipant:
        print(f"[DEBUG] User {message.from_user.id} BLOCKED by Force Sub in {message.chat.id}")
        chat_id = message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        
        btn_text = _["S_B_9"] if "S_B_9" in _ else "Join Channel"
        text = _["force_sub_text"] if "force_sub_text" in _ else "To use this bot, you must join our support channel first!"
        
        buttons = [[InlineKeyboardButton(text=btn_text, url=SUPPORT_CHANNEL)]]
        await message.reply_text(
            text=f"Hey {message.from_user.mention},\n\n{text}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        message.stop_propagation()
    except Exception:
        pass
