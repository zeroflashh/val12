import asyncio
import importlib

from pyrogram import idle
from pyrogram.errors import FloodWait
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ValentinMusic import LOGGER, app, userbot
from ValentinMusic.core.call import Anony
from ValentinMusic.misc import sudo
from ValentinMusic.plugins import ALL_MODULES
from ValentinMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    # Handle FloodWait from Telegram bot auth
    max_flood_retries = 3
    flood_wait_done = False
    for attempt in range(max_flood_retries):
        try:
            await app.start()
            flood_wait_done = True
            break
        except FloodWait as e:
            wait_seconds = e.seconds
            LOGGER(__name__).warning(f"FloodWait {wait_seconds}s on bot auth (attempt {attempt+1}/{max_flood_retries}). Waiting...")
            await asyncio.sleep(wait_seconds + 10)

    if not flood_wait_done:
        LOGGER(__name__).error("Max flood wait retries exceeded. Exiting.")
        exit()

    for all_module in ALL_MODULES:
        importlib.import_module("ValentinMusic.plugins" + all_module)
    LOGGER("ValentinMusic.plugins").info("Successfully Imported Modules...")

    if hasattr(config, "COOKIES_URL") and config.COOKIES_URL:
        try:
            from ValentinMusic.platforms import YouTube
            await YouTube.save_cookies(config.COOKIES_URL)
        except Exception as e:
            LOGGER("ValentinMusic").error(f"Failed to fetch cookies: {e}")

    await userbot.start()
    await Anony.start()
    try:
        await Anony.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ValentinMusic").error(
            "Please turn on the videochat of your log group\\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Anony.decorators()
    LOGGER("ValentinMusic").info(
        "ValentinMusicMusic Bot Started Successfully.\n\nDon't forget to visit @Anaavaran"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("ValentinMusic").info("Stopping ValentinMusic Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
