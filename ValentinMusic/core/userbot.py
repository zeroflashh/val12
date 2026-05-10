import asyncio
import binascii
import base64
from pyrogram import Client, errors
from pyrogram.errors import FloodWait

import config

from ..log import LOGGER

assistants = []
assistantids = []


def _valid_session(session_str):
    if not session_str:
        return False
    s = str(session_str)
    try:
        base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
        return True
    except Exception:
        return False


class Userbot(Client):
    def __init__(self):
        if _valid_session(config.STRING1):
            self.one = Client(
                name="ValentinMusicAss1",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING1),
                no_updates=True,
            )
        else:
            self.one = None

        if _valid_session(config.STRING2):
            self.two = Client(
                name="ValentinMusicAss2",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING2),
                no_updates=True,
            )
        else:
            self.two = None

        if _valid_session(config.STRING3):
            self.three = Client(
                name="ValentinMusicAss3",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING3),
                no_updates=True,
            )
        else:
            self.three = None

        if _valid_session(config.STRING4):
            self.four = Client(
                name="ValentinMusicAss4",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING4),
                no_updates=True,
            )
        else:
            self.four = None

        if _valid_session(config.STRING5):
            self.five = Client(
                name="ValentinMusicAss5",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING5),
                no_updates=True,
            )
        else:
            self.five = None

    async def start(self):
        LOGGER(__name__).info(f"Starting Assistants...")
        from pyrogram.errors import FloodWait
        import asyncio

        if config.STRING1 and self.one:
            try:
                for attempt in range(3):
                    try:
                        await self.one.start()
                        break
                    except FloodWait as e:
                        if attempt == 2: raise
                        LOGGER(__name__).warning(f"Assistant 1: FloodWait {e.seconds}s. Waiting...")
                        await asyncio.sleep(e.seconds + 5)
            except binascii.Error:
                LOGGER(__name__).error("Assistant 1: Invalid session string.")
                self.one = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 1 failed: {e}")
                self.one = None
            else:
                try:
                    await self.one.join_chat("Anaavaran")
                    await self.one.join_chat("Anaavaran_Support")
                except: pass
                assistants.append(1)
                try:
                    await self.one.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error("Assistant 1 failed to access log group.")
                self.one.id = self.one.me.id
                self.one.name = self.one.me.mention
                self.one.username = self.one.me.username
                assistantids.append(self.one.id)
                LOGGER(__name__).info(f"Assistant 1 Started as {self.one.name}")

        if config.STRING2 and self.two:
            try:
                for attempt in range(3):
                    try:
                        await self.two.start()
                        break
                    except FloodWait as e:
                        if attempt == 2: raise
                        LOGGER(__name__).warning(f"Assistant 2: FloodWait {e.seconds}s. Waiting...")
                        await asyncio.sleep(e.seconds + 5)
            except binascii.Error:
                LOGGER(__name__).error("Assistant 2: Invalid session string.")
                self.two = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 2 failed: {e}")
                self.two = None
            else:
                try:
                    await self.two.join_chat("Anaavaran")
                    await self.two.join_chat("Anaavaran_Support")
                except: pass
                assistants.append(2)
                try:
                    await self.two.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error("Assistant 2 failed to access log group.")
                self.two.id = self.two.me.id
                self.two.name = self.two.me.mention
                self.two.username = self.two.me.username
                assistantids.append(self.two.id)
                LOGGER(__name__).info(f"Assistant 2 Started as {self.two.name}")

        if config.STRING3 and self.three:
            try:
                for attempt in range(3):
                    try:
                        await self.three.start()
                        break
                    except FloodWait as e:
                        if attempt == 2: raise
                        LOGGER(__name__).warning(f"Assistant 3: FloodWait {e.seconds}s. Waiting...")
                        await asyncio.sleep(e.seconds + 5)
            except binascii.Error:
                LOGGER(__name__).error("Assistant 3: Invalid session string.")
                self.three = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 3 failed: {e}")
                self.three = None
            else:
                try:
                    await self.three.join_chat("Anaavaran")
                    await self.three.join_chat("Anaavaran_Support")
                except: pass
                assistants.append(3)
                try:
                    await self.three.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error("Assistant 3 failed to access log group.")
                self.three.id = self.three.me.id
                self.three.name = self.three.me.mention
                self.three.username = self.three.me.username
                assistantids.append(self.three.id)
                LOGGER(__name__).info(f"Assistant 3 Started as {self.three.name}")

        if config.STRING4 and self.four:
            try:
                for attempt in range(3):
                    try:
                        await self.four.start()
                        break
                    except FloodWait as e:
                        if attempt == 2: raise
                        LOGGER(__name__).warning(f"Assistant 4: FloodWait {e.seconds}s. Waiting...")
                        await asyncio.sleep(e.seconds + 5)
            except binascii.Error:
                LOGGER(__name__).error("Assistant 4: Invalid session string.")
                self.four = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 4 failed: {e}")
                self.four = None
            else:
                try:
                    await self.four.join_chat("Anaavaran")
                    await self.four.join_chat("Anaavaran_Support")
                except: pass
                assistants.append(4)
                try:
                    await self.four.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error("Assistant 4 failed to access log group.")
                self.four.id = self.four.me.id
                self.four.name = self.four.me.mention
                self.four.username = self.four.me.username
                assistantids.append(self.four.id)
                LOGGER(__name__).info(f"Assistant 4 Started as {self.four.name}")

        if config.STRING5 and self.five:
            try:
                for attempt in range(3):
                    try:
                        await self.five.start()
                        break
                    except FloodWait as e:
                        if attempt == 2: raise
                        LOGGER(__name__).warning(f"Assistant 5: FloodWait {e.seconds}s. Waiting...")
                        await asyncio.sleep(e.seconds + 5)
            except binascii.Error:
                LOGGER(__name__).error("Assistant 5: Invalid session string.")
                self.five = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 5 failed: {e}")
                self.five = None
            else:
                try:
                    await self.five.join_chat("Anaavaran")
                    await self.five.join_chat("Anaavaran_Support")
                except: pass
                assistants.append(5)
                try:
                    await self.five.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error("Assistant 5 failed to access log group.")
                self.five.id = self.five.me.id
                self.five.name = self.five.me.mention
                self.five.username = self.five.me.username
                assistantids.append(self.five.id)
                LOGGER(__name__).info(f"Assistant 5 Started as {self.five.name}")

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Assistants...")
        try:
            if self.one:
                await self.one.stop()
            if self.two:
                await self.two.stop()
            if self.three:
                await self.three.stop()
            if self.four:
                await self.four.stop()
            if self.five:
                await self.five.stop()
        except:
            pass
