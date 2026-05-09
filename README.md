<div align="center">

<h2>ValentinMusic</h2>

<b>Telegram Group Calls Streaming Bot</b><br>
Supports YouTube, Spotify, Resso, Apple Music, SoundCloud and M3U8 links.

<a href="https://github.com/zeroflashh/val12/stargazers">
    <img src="https://img.shields.io/github/stars/zeroflashh/val12?color=blueviolet&logo=github&logoColor=black&style=for-the-badge" alt="Stars"/>
</a>
<a href="https://github.com/zeroflashh/val12/network/members">
    <img src="https://img.shields.io/github/forks/zeroflashh/val12?color=blueviolet&logo=github&logoColor=black&style=for-the-badge" alt="Forks"/>
</a>
<a href="https://github.com/zeroflashh/val12/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"/>
</a>
<a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Written%20in-Python-blue?style=for-the-badge&logo=python" alt="Python"/>
</a>
<br>

<img src="https://github.com/zeroflashh/val12/blob/master/.github/Valentin.jpg" width="720" height="auto">

ValentinMusic lets you stream high-quality and low-latency audio and video playback into telegram group video chats.<br>
Built with Python, Pyrogram, and Py-TgCalls, it’s optimized for reliability and easy deployment on VPS or Docker.
</div>

<hr>

<h2>🔥 Features</h2>

- 🎧 Stream low-latency audio in real time to <b>Telegram group video chats</b>
- 🌐 Supports multiple platforms like <b>YouTube, Spotify, Apple Music, SoundCloud</b>
- ⚡ Advanced queue management with auto-play
- ⚙️ Easy deployment — works on Local, VPS, or Docker
- ❤️ Built with Python
<hr>

<h2>☁️ Deployment Guide</h2>

<h3>🐳 Docker Deployment (Recommended)</h3>

1. **Clone the Project:**
   ```bash
   git clone https://github.com/zeroflashh/val12
   cd val12
   ```
2. **Configure Environment:**
   Create a `.env` file and add your credentials (API_ID, API_HASH, BOT_TOKEN, MONGO_DB_URI, STRING_SESSION, etc.).
3. **Start the Bot:**
   ```bash
   docker compose up -d --build
   ```
4. **Stop the Bot:**
   ```bash
   docker compose down
   ```

<h3>🛠️ Manual Setup (VPS/Local)</h3>

<h4>🐧 Linux/macOS</h4>

```bash
git clone https://github.com/zeroflashh/val12 && cd val12

# Install uv
curl -Ls https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Install dependencies
uv sync --frozen

# Configure environment variables
# Edit .env with your credentials

# Start the bot
bash start
```

<h4>🪟 Windows (PowerShell)</h4>

```bash
git clone https://github.com/zeroflashh/val12 && cd val12

# Install uv
irm https://astral.sh/uv/install.ps1 | iex

# Install dependencies
uv sync --frozen

# Configure environment variables
# Edit .env with your credentials

# Start the bot
uv run python3 -m ValentinMusic

> ⭐ or use Git Bash or WSL to run `bash start`.
```

<hr>

<h2>⚙️ Configuration</h2>

Edit <code>.env</code> (or set variables in your hosting environment):
<details>
    <summary>Here's an example of the .env file</summary>

```env
API_ID=123456
API_HASH=abcdef1234567890
BOT_TOKEN=123456:ABC-DEF
OWNER_ID=123456789
LOGGER_ID=-1001234567890
MONGO_URL=mongodb+srv://
SESSION=BQgfh...AA
```

> 📝 Check <a href="https://github.com/zeroflashh/val12/blob/master/config.py">config.py</a> for all available options.
</details>

<hr>

<h2>🧐 Usage & Commands</h2>

1. Add the bot to your Telegram group.  
2. Promote it to <b>admin</b> with invite users permission.  
3. Use commands in the chat to control playback:
<details>
    <summary>Music Play Commands Overview</summary>
    <pre>
/play [Name/Link] -> Start streaming audio on voice chat
/vplay [Name/Link] -> Start streaming video on voice chat
/playforce -> Force play (stops current and starts new track)
/pause -> Pause current music stream
/resume -> Resume paused music stream
/skip -> Skip to next track in queue
/stop or /end -> Stop music and clear the entire queue
/queue -> Show upcoming tracks in queue
/shuffle -> Randomly shuffle music queue
/volume [1-200] -> Adjust the bot's volume level
/loop [enable/disable] -> Toggle loop for current track
/stream [link] -> Stream audio/video from direct link (m3u8/index)
/seek [seconds] -> Move the stream forward
/seekback [seconds] -> Move the stream backward
/speed -> Change playback speed (0.5x to 2.0x)
    </pre>
</details>

<hr>

<h2>❤️ Contributing</h2>

Contributions are welcome!

1. Fork the repository.  
2. Create your branch: <code>git checkout -b feature/new</code>.  
4. Commit changes: <code>git commit -m 'New feature'</code>.  
5. Push: <code>git push origin feature/new</code>
6. Open a Pull Request.

<hr>

<h2>🗒️ License</h2>

This project is licensed under the <b>MIT License</b> — see <a href="https://github.com/zeroflashh/val12/blob/master/LICENSE">LICENSE</a> for details.

<hr>

<h2>🤞 Updates and support</h2>

- <a href="https://Anaavaran.t.me">Updates channel</a>
- <a href="https://AnaavaranOT.t.me">Support group</a>

<hr>

<h2>👀 Acknowledgements</h2>

- Inspired by other open-source Telegram music bots (Yukki, AnonXMusic and others).
- Thanks to all the <a href="https://github.com/zeroflashh/val12/graphs/contributors">contributors</a>.

<hr>

<div align="center">

⭐ Enjoying the tunes? <b>Star the repo</b> — feedback keeps the rhythm going!

</div>
