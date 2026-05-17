import asyncio
import binascii
import base64
from pyrogram import Client, errors
from pyrogram.errors import FloodWait

import config

from ..log import LOGGER

assistants = []
assistantids = []

STRING_ATTRS = ["STRING1", "STRING2", "STRING3", "STRING4", "STRING5"]
ASSISTANT_ATTRS = ["one", "two", "three", "four", "five"]
CHANNELS = ["Anaavaran", "Anaavaran_Support"]


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
        self.clients: list[Client | None] = []
        for idx, attr in enumerate(STRING_ATTRS, start=1):
            session = getattr(config, attr, None)
            if _valid_session(session):
                client = Client(
                    name=f"ValentinMusicAss{idx}",
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=str(session),
                    no_updates=True,
                )
            else:
                client = None
            self.clients.append(client)
            setattr(self, ASSISTANT_ATTRS[idx - 1], client)

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")
        for idx, client in enumerate(self.clients, start=1):
            if not client:
                continue
            try:
                for attempt in range(3):
                    try:
                        await client.start()
                        break
                    except FloodWait as e:
                        if attempt == 2:
                            raise
                        LOGGER(__name__).warning(
                            f"Assistant {idx}: FloodWait {e.seconds}s. Waiting..."
                        )
                        await asyncio.sleep(e.seconds + 5)
            except binascii.Error:
                LOGGER(__name__).error(f"Assistant {idx}: Invalid session string.")
                self.clients[idx - 1] = None
                continue
            except Exception as e:
                LOGGER(__name__).error(f"Assistant {idx} failed: {e}")
                self.clients[idx - 1] = None
                continue

            for channel in CHANNELS:
                try:
                    await client.join_chat(channel)
                except Exception:
                    pass
            assistants.append(idx)
            try:
                await client.send_message(config.LOGGER_ID, "Assistant Started")
            except Exception:
                LOGGER(__name__).error(f"Assistant {idx} failed to access log group.")
            client.id = client.me.id
            client.name = client.me.mention
            client.username = client.me.username
            assistantids.append(client.id)
            LOGGER(__name__).info(f"Assistant {idx} Started as {client.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        for client in self.clients:
            if client:
                try:
                    await client.stop()
                except Exception:
                    pass
