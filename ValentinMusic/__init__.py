import sys
import email.message

if 'cgi' not in sys.modules:
    class DummyCGI:
        @staticmethod
        def parse_header(line):
            m = email.message.Message()
            m['content-type'] = line
            params = m.get_params() or []
            pdict = {k: v for k, v in params[1:]} if len(params) > 1 else {}
            return m.get_content_type(), pdict

    sys.modules['cgi'] = DummyCGI

import httpx
orig_post = httpx.post
def patched_post(*args, **kwargs):
    kwargs.pop('proxy', None)
    kwargs.pop('proxies', None)
    return orig_post(*args, **kwargs)
httpx.post = patched_post

orig_get = httpx.get
def patched_get(*args, **kwargs):
    kwargs.pop('proxy', None)
    kwargs.pop('proxies', None)
    return orig_get(*args, **kwargs)
httpx.get = patched_get

orig_async_init = httpx.AsyncClient.__init__
def patched_async_init(self, *args, **kwargs):
    kwargs.pop('proxy', None)
    kwargs.pop('proxies', None)
    return orig_async_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = patched_async_init

import pyromod
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
