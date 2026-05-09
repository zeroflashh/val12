import asyncio
from pyrogram.errors import FloodWait, MessageDeleteForbidden

async def delete_after_10(message):
    await asyncio.sleep(10)
    try:
        await message.delete()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.delete()
    except MessageDeleteForbidden:
        pass
    except Exception:
        pass
