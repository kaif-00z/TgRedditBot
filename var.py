#    This file is part of the TgRedditBot distribution.
#    Copyright (c) 2022 Kaif_00z
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/kaif-00z/TgRedditBot/blob/main/License> .


from decouple import config
from dotenv import load_dotenv

load_dotenv()


class Var:
    # Telegram Credentials
    API_ID = config("API_ID", cast=int)
    API_HASH = config("API_HASH", default=None)
    BOT_TOKEN = config("BOT_TOKEN", default=None)
    OWNER = config("OWNER", default=None)

    # Reddit Credantials
    REDDIT_CLIENT_ID = config("REDDIT_CLIENT_ID", default=None)
    REDDIT_CLIENT_SECRET = config("REDDIT_CLIENT_SECRET", default=None)
    REDDIT_PASSWORD = config("REDDIT_PASSWORD", default=None)
    REDDIT_USERNAME = config("REDDIT_USERNAME", default=None)

    # Redis Credantials
    REDIS_URI = config("REDIS_URI", default=None)
    REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)

    # Async Praw Logging
    ASYNC_PRAW_DEBUG = config("ASYNC_PRAW_DEBUG", default=False, cast=bool)
