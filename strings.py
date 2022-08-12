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


START = "Hi {},\nI am Normal Telegram Bot Which Give You Permission To Interact With Reddit From Telegram, Also I Can Stream Subreddit(s) On Telegram."

ABOUT = """
**⏱ Uptime** : `{}`
**💡 Version** : `v0.0.1@beta-build.69.1`

• **🐍 Python**: `{}`
• **✈️ Telethon**: `{}`
• **🏔️ Asyncpraw**: `{}`
• **💻 Server**: `{}`
• **📖 Source Code** : {}

~ **Developer**  __@Kaif_00z__
"""

HELP = """
• `/start` - __To start The Bot.__

• `/restart` - __Restart The Bot and also update the source code.__

• `/mycommunites` - __Return A list of your subscribed Subreddits.__

• `/trusted` - __Returns A list of your trusted user.__

• `/friends` - __Returns A list of your friends.__

• `/blocked` - __Returns A list of blocked user.__

• `/pin <link | optional>` - __Will Pin the latest submission, if you will give link then it will pin the given submission in respective subreddit.__

• `/unpin <link | optional>` - __Will UnPin the latest submission, if you will give link then it will unpin the given submission in respective subreddit.__

• `/feed <no. of post | optional>` - __Will give the submission information present in your feed.__

• `/watch <username of subreddit>` - __Will Notify When A New Submission Come In The Following Subreddit.__
__ex-__ `/watch redditdev`

• `/unwatch <username of subreddit>` - __Will Remove The Following Subreddit From Watch List.__
__ex-__ `/unwatch redditdev`

• `/listwatch` - __To Get The List of Subreddit Which are In Watch.__

• `/join <username of subreddit>` - __To Subscribe the subreddit.__
__ex-__ `/join redditdev`

• `/info <username of subreddit>` - __To Get Information of the given subreddit.__
__ex-__ `/info redditdev`
"""

PRO = "`Proccesing...`"

AD = "`⚔️ Access Denied ⚔️`"

SUB_INFO = """
**📛 Name** : `{}`
**🆔 Id** : `{}`
**🔗 Link** : {}
**📜 Description**: `{}`
**📝 Created** : `{}`
**🔞 Nsfw** : `{}`
**🙊 Spoilers** : `{}`
**👥 Subscribers** : `{}`
**👨🏻‍🔧 I Am Moderator** : `{}`
**💥 I Am a Subscriber** : `{}`
**🚫 I Am Banned** : `{}`
"""
