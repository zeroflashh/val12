<p align="center">
  <img src="https://telegra.ph/file/32ebdec3530b5d00ff215.jpg" width="200" height="200" style="border-radius: 50%;">
</p>

<h1 align="center">
  <b>✧ VALENTIN MUSIC BOT ✧</b>
</h1>

<p align="center">
  <a href="https://github.com/zeroflashh/val12">
    <img src="https://img.shields.io/github/v/release/zeroflashh/val12?color=FF3E3E&style=for-the-badge" alt="Release">
  </a>
  <a href="https://t.me/Anaavaran">
    <img src="https://img.shields.io/badge/Support-Channel-blue?style=for-the-badge&logo=telegram" alt="Support Channel">
  </a>
</p>

<p align="center">
  <b>ValentinMusic</b> is a premium, ultra-fast Telegram Music Bot designed for high-fidelity audio and video streaming. 
  Built on <b>Pyrogram</b> and <b>Py-TgCalls</b>, it offers a seamless experience with extensive platform support.
</p>

---

## 🚀 Deployment (Docker/VPS)

ValentinMusic is optimized for containerized environments. Follow these steps for a perfect deployment.

### 📦 Prerequisites
- Docker & Docker Compose installed.
- A `mongoDB` URI and Telegram `API_ID/HASH`.

### 🛠️ Step-by-Step Setup

1. **Clone the Project:**
   ```bash
   git clone https://github.com/zeroflashh/val12
   cd val12
   ```

2. **Configure Environment:**
   Create a `.env` file and add your credentials:
   ```env
   API_ID=123456
   API_HASH=abcdef123456...
   BOT_TOKEN=12345:ABCDE...
   MONGO_DB_URI=mongodb+srv://...
   OWNER_ID=5329521369
   STRING_SESSION=BAGxz8MAe...
   ```

3. **Start the Bot (Run in Background):**
   ```bash
   docker compose up -d --build
   ```

4. **Monitor Logs:**
   ```bash
   docker compose logs -f
   ```

5. **Stop the Bot:**
   ```bash
   docker compose down
   ```

6. **Restart the Bot:**
   ```bash
   docker compose restart
   ```

---

## 🔑 Session Generation

You can generate your **Pyrogram v2** or **Telethon** session string directly via Docker without installing anything locally:

```bash
docker compose run --rm valentin uv run python3 -m ValentinMusic.plugins.tools.genstr
```

---

## 🎵 Complete Play Module Commands

| Command | Action |
| :--- | :--- |
| `/play [Query/Link]` | Start streaming audio in the voice chat |
| `/vplay [Query/Link]` | Start streaming video in the voice chat |
| `/playforce` | Stops current playback and starts new track instantly |
| `/pause` | Pauses the current music/video stream |
| `/resume` | Resumes the paused stream |
| `/skip` | Skips to the next track in the queue |
| `/stop` | Stops the stream and clears the entire queue |
| `/end` | Alternative for /stop |
| `/queue` | Displays the list of upcoming tracks |
| `/shuffle` | Randomizes the current music queue |
| `/volume [1-200]` | Dynamically adjusts the bot's volume level |
| `/loop [enable/disable]` | Toggles repeat mode for the current track |
| `/seek [seconds]` | Jumps forward in the stream |
| `/seekback [seconds]` | Jumps backward in the stream |
| `/speed` | Opens the playback speed control panel (0.5x - 2.0x) |
| `/stream [URL]` | Streams direct links (m3u8, index, etc.) |
| `/cplay` | Play music in a linked channel |

---

## 🛠️ Administrative & Sudo Tools

- **Group Settings:** `/settings` - Configure your group's bot behavior.
- **Language:** `/lang` - Switch between 8+ supported languages.
- **Maintenance:** `/maintenance [enable/disable]` - Restricted access mode.
- **Global Ban:** `/gban` - Protect your chats from malicious users.
- **Statistics:** `/stats` - View bot performance and usage data.

---

<p align="center">
  <b>Powered by <a href="https://t.me/Anaavaran">Anaavaran</a></b><br>
  <i>Bringing Premium Music to your Telegram Communities.</i>
</p>
