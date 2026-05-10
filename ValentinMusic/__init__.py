# pyrofork is a Pyrogram fork with pyromod listener patches built-in.
# No separate pyromod import needed.
from ValentinMusic.core.bot import Anony
from ValentinMusic.core.dir import dirr
from ValentinMusic.core.git import git
from ValentinMusic.core.userbot import Userbot
from ValentinMusic.misc import dbb, heroku

from .log import LOGGER

dirr()
git()
dbb()
heroku()

app = Anony()
userbot = Userbot()


from .platforms import *

Carbon = CarbonAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
