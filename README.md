# Valentin Music Bot

Valentin is a fast and powerful Telegram Music Bot based on Pyrogram and Py-TgCalls.

## 🚀 Deployment

### VPS/Docker

1. **Install Docker & Docker Compose** (if not already installed).
2. **Configure Environment Variables:**
   Create a `.env` file with your API credentials (API_ID, API_HASH, BOT_TOKEN, MONGO_DB_URI, STRING_SESSION, etc.).
3. **Start the Bot:**
   ```bash
   docker compose up -d --build
   ```
4. **Stop the Bot:**
   ```bash
   docker compose down
   ```

### String Session Generation

You can generate your string session directly via Docker:

```bash
docker compose run --rm valentin uv run python3 -m ValentinMusic.plugins.tools.genstr
```
Alternatively, if you have python installed locally:
```bash
uv run python3 -m ValentinMusic.plugins.tools.genstr
```

## 🎵 Commands

### Play Commands
- **/play [Name/Link]** - Start streaming audio on voice chat.
- **/vplay [Name/Link]** - Start streaming video on voice chat.
- **/playforce** - Force play (stops current and starts new track).
- **/pause** - Pause the current music stream.
- **/resume** - Resume the paused music stream.
- **/skip** - Skip current track to the next in queue.
- **/stop** or **/end** - Stop music and clear the entire queue.
- **/queue** - Show upcoming tracks in the music queue.
- **/shuffle** - Randomly shuffle the music queue.
- **/volume [1-200]** - Adjust the bot's volume level.
- **/loop [enable/disable]** - Toggle loop for current track.
- **/stream [link]** - Stream audio/video from a direct link (m3u8/index).
- **/seek [seconds]** - Move the stream forward.
- **/seekback [seconds]** - Move the stream backward.
- **/speed** - Change playback speed (0.5x to 2.0x).

---
**Powered by @Anaavaran**
