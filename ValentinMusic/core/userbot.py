import binascii
import base64

from pyrogram import Client

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

        if config.STRING1 and self.one:
            try:
                await self.one.start()
            except binascii.Error:
                LOGGER(__name__).error(
                    "Assistant 1: Invalid session string. Skipping. Regenerate via /genstr command."
                )
                self.one = None
                config.STRING1 = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 1 failed to start: {e}")
                self.one = None
                config.STRING1 = None
            else:
                try:
                    await self.one.join_chat("Anaavaran")
                    await self.one.join_chat("Anaavaran")
                except:
                    pass
                assistants.append(1)
                try:
                    await self.one.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error(
                        "Assistant Account 1 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                    )
                    exit()
                self.one.id = self.one.me.id
                self.one.name = self.one.me.mention
                self.one.username = self.one.me.username
                assistantids.append(self.one.id)
                LOGGER(__name__).info(f"Assistant Started as {self.one.name}")

        if config.STRING2 and self.two:
            try:
                await self.two.start()
            except binascii.Error:
                LOGGER(__name__).error(
                    "Assistant 2: Invalid session string. Skipping. Regenerate via /genstr command."
                )
                self.two = None
                config.STRING2 = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 2 failed to start: {e}")
                self.two = None
                config.STRING2 = None
            else:
                try:
                    await self.two.join_chat("Anaavaran")
                    await self.two.join_chat("Anaavaran")
                except:
                    pass
                assistants.append(2)
                try:
                    await self.two.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error(
                        "Assistant Account 2 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                    )
                    exit()
                self.two.id = self.two.me.id
                self.two.name = self.two.me.mention
                self.two.username = self.two.me.username
                assistantids.append(self.two.id)
                LOGGER(__name__).info(f"Assistant Two Started as {self.two.name}")

        if config.STRING3 and self.three:
            try:
                await self.three.start()
            except binascii.Error:
                LOGGER(__name__).error(
                    "Assistant 3: Invalid session string. Skipping. Regenerate via /genstr command."
                )
                self.three = None
                config.STRING3 = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 3 failed to start: {e}")
                self.three = None
                config.STRING3 = None
            else:
                try:
                    await self.three.join_chat("Anaavaran")
                    await self.three.join_chat("Anaavaran")
                except:
                    pass
                assistants.append(3)
                try:
                    await self.three.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error(
                        "Assistant Account 3 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                    )
                    exit()
                self.three.id = self.three.me.id
                self.three.name = self.three.me.mention
                self.three.username = self.three.me.username
                assistantids.append(self.three.id)
                LOGGER(__name__).info(f"Assistant Three Started as {self.three.name}")

        if config.STRING4 and self.four:
            try:
                await self.four.start()
            except binascii.Error:
                LOGGER(__name__).error(
                    "Assistant 4: Invalid session string. Skipping. Regenerate via /genstr command."
                )
                self.four = None
                config.STRING4 = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 4 failed to start: {e}")
                self.four = None
                config.STRING4 = None
            else:
                try:
                    await self.four.join_chat("Anaavaran")
                    await self.four.join_chat("Anaavaran")
                except:
                    pass
                assistants.append(4)
                try:
                    await self.four.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error(
                        "Assistant Account 4 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                    )
                    exit()
                self.four.id = self.four.me.id
                self.four.name = self.four.me.mention
                self.four.username = self.four.me.username
                assistantids.append(self.four.id)
                LOGGER(__name__).info(f"Assistant Four Started as {self.four.name}")

        if config.STRING5 and self.five:
            try:
                await self.five.start()
            except binascii.Error:
                LOGGER(__name__).error(
                    "Assistant 5: Invalid session string. Skipping. Regenerate via /genstr command."
                )
                self.five = None
                config.STRING5 = None
            except Exception as e:
                LOGGER(__name__).error(f"Assistant 5 failed to start: {e}")
                self.five = None
                config.STRING5 = None
            else:
                try:
                    await self.five.join_chat("Anaavaran")
                    await self.five.join_chat("Anaavaran")
                except:
                    pass
                assistants.append(5)
                try:
                    await self.five.send_message(config.LOGGER_ID, "Assistant Started")
                except:
                    LOGGER(__name__).error(
                        "Assistant Account 5 has failed to access the log Group. Make sure that you have added your assistant to your log group and promoted as admin!"
                    )
                    exit()
                self.five.id = self.five.me.id
                self.five.name = self.five.me.mention
                self.five.username = self.five.me.username
                assistantids.append(self.five.id)
                LOGGER(__name__).info(f"Assistant Five Started as {self.five.name}")

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
