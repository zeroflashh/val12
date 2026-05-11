import re

from pyrogram import filters

# ============================================================
# REQUIRED CREDENTIALS - Fill in your values below
# ============================================================

# Get from https://my.telegram.org/apps
API_ID = 7949855
API_HASH = "ea4403a7f9496b9b39fdb6401f32c46b"

# Get from @BotFather
BOT_TOKEN = "6173918825:AAEyS1Wc9d_v17cOJn0rWdXWLL47cChgvKo"

# Get from cloud.mongodb.com
MONGO_DB_URI = "mongodb+srv://zero:zero@zero.y5pa4sd.mongodb.net/?appName=zero"

# Chat ID of log group (with -100 prefix for supergroups)
LOGGER_ID = -1001615517255

# Your Telegram user ID (get from @userinfobot or /id command)
OWNER_ID = 5329521369

# ============================================================
# ASSISTANT SESSION STRINGS
# ============================================================
# Generate via: python gen_str.py
# Or via bot: /genstr command

STRING1 = "BAB5Th8AeeOaatdXLV1F-2dhv_xCzfj16n3AZmNyMrspRgbYgVWV00Es7YFVGbfsPM9gjGrlBPCH1Asa7pWL1E9O4RkmE3be_qTUyRlj77MYx1Lk9hTGMz-cVdgfTVNHQM76zg-nUu2rrASpMxArhpMneWA98yG3Ra6bGgO6MZKWm14y4ixfVH8FPdZWhpwycqMPTULV4IO4cbUGw8weK14yevf2w2cHfMUUFu2cQ4mGc4JN9IAc8f08iW7q88DY66U5IAOB6IMZJiS0YBFHAXP0eGnjRV7BrIDQ_nxb5lgDY_JMGN5BiyuUm4Z0HLUvkF-H-f2hOS1V9SO6m4Hq8X_0MOuEZwAAAAFtSVWxAA"
STRING2 = None
STRING3 = None
STRING4 = None
STRING5 = None

# ============================================================
# CONFIGURATION OPTIONS
# ============================================================

# Max play duration in minutes
DURATION_LIMIT_MIN = 720

# Upstream repo for auto-updates
UPSTREAM_REPO = "https://github.com/zeroflashh/val12"
UPSTREAM_BRANCH = "main"
GIT_TOKEN = None  # Fill if upstream repo is private
from os import getenv
COOKIES_URL = getenv("COOKIES_URL", None)
if COOKIES_URL:
    COOKIES_URL = [url for url in COOKIES_URL.split(" ") if url ]

# Support links
SUPPORT_CHANNEL = "https://t.me/Anaavaran"
SUPPORT_CHAT = "https://t.me/AnaavaranOT"

# Auto-leave inactive chats
AUTO_LEAVING_ASSISTANT = False

# Playlist fetch limit
PLAYLIST_FETCH_LIMIT = 100

# Telegram file size limits (in bytes)
TG_AUDIO_FILESIZE_LIMIT = 4294967296
TG_VIDEO_FILESIZE_LIMIT = 4294967296

# ============================================================
# IMAGE URLs (thumbnails, banners)
# ============================================================

START_IMG_URL = "https://telegra.ph/file/32ebdec3530b5d00ff215.jpg"
PING_IMG_URL = "https://telegra.ph/file/9d0ceecf52dc224624d36.jpg"
PLAYLIST_IMG_URL = "https://telegra.ph/file/053e94eed2eff8349e00a.jpg"
STATS_IMG_URL = "https://telegra.ph/file/40788ee0f4dd9bc27060e.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/86eda736f5f2cf9aa3e8b.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/3f8cdf58f42b38ea01249.jpg"
STREAM_IMG_URL = "https://telegra.ph/file/575481164847bb86c195b.jpg"
YOUTUBE_IMG_URL = "https://telegra.ph/file/6b95d8e185bc728a2a570.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"

# ============================================================
# INTERNAL STATE (do not edit)
# ============================================================

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


# ============================================================
# VALIDATION
# ============================================================

if SUPPORT_CHANNEL:
    if not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - SUPPORT_CHANNEL must start with https://")

if SUPPORT_CHAT:
    if not re.match(r"(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - SUPPORT_CHAT must start with https://")
