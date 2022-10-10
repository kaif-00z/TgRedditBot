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


import os
import sys
from datetime import datetime as dt
from logging import DEBUG, INFO, FileHandler, StreamHandler, basicConfig, getLogger
from platform import python_version, release, system
from traceback import format_exc

from asyncpraw import Reddit
from asyncpraw.const import __version__ as praw_version
from redis import Redis
from telethon import Button, TelegramClient, events
from telethon import __version__ as telethon_version
from telethon.tl.types import DocumentAttributeVideo
from telethon.utils import get_display_name

from helper import *
from strings import *
from var import Var

file = "TgRedditBot.log"
if os.path.exists(file):
    os.remove(file)

basicConfig(
    format="[%(levelname)s] [%(asctime)s] [%(name)s] : %(message)s",
    handlers=[FileHandler(file), StreamHandler()],
    level=INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
)
LOGS = getLogger("TgRedditBot")
TelethonLogger = getLogger("Telethon")
TelethonLogger.setLevel(INFO)


for logger_name in ("asyncpraw", "asyncprawcore"):
    logger = getLogger(logger_name)
    if Var.ASYNC_PRAW_DEBUG:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)


try:
    LOGS.info("Trying Connect With Telegram")
    bot = TelegramClient(None, Var.API_ID, Var.API_HASH).start(bot_token=Var.BOT_TOKEN)
    LOGS.info("Successfully Connected with Telegram")
except Exception as e:
    LOGS.critical("Something Went Wrong While Connecting To Telegram")
    LOGS.error(str(e))
    exit()

try:
    LOGS.info("Trying Connect With Reddit")
    reddit = Reddit(
        client_id=Var.REDDIT_CLIENT_ID,
        client_secret=Var.REDDIT_CLIENT_SECRET,
        user_agent="botscript by t.me/kaif_00z",
        username=Var.REDDIT_USERNAME,
        password=Var.REDDIT_PASSWORD,
    )
    LOGS.info("Successfully Connected with Reddit")
except Exception as exc:
    LOGS.critical("Something Went Wrong While Connecting To Reddit")
    LOGS.error(str(exc))
    exit()

try:
    LOGS.info("Trying Connect With Redis database")
    redis_info = Var.REDIS_URI.split(":")
    dB = Redis(
        host=redis_info[0],
        port=redis_info[1],
        password=Var.REDIS_PASSWORD,
        charset="utf-8",
        decode_responses=True,
    )
    LOGS.info("successfully connected to Redis database")
except Exception as eo:
    LOGS.critical("Something Went Wrong While Connecting To Redis")
    LOGS.error(str(eo))
    exit()

UPTIME = dt.now()
FUTURE = {}
# STREAM_INBOX = []

# ================Show Case===============================================


@bot.on(events.NewMessage(incoming=True, pattern="^/start$"))
async def start(event):
    btn = [
        [Button.url("Updates Channel", url="t.me/BotsBakery")],
        [
            Button.url("Developer", url="t.me/kaif_00z"),
            Button.inline("Info", data="inf"),
        ],
        [Button.inline("Help", data="hlp")],
    ]
    await event.reply(START.format(get_display_name(event.sender)), buttons=btn)


@bot.on(events.NewMessage(incoming=True, pattern="^/help$"))
async def hlp(event):
    await event.reply(HELP)


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("hlp")))
async def help(event):
    await event.edit(HELP)


@bot.on(events.NewMessage(incoming=True, pattern="^/logs$"))
async def loggs(event):
    xx = await event.reply(PRO)
    await event.reply(
        file=file,
        force_document=True,
        thumb="thumb.jpg",
    )
    await xx.delete()


async def about(event, edit=False):
    x = ABOUT.format(
        ts(int((dt.now() - UPTIME).seconds) * 1000),
        f"{python_version()}",
        telethon_version,
        praw_version,
        f"{system()} {release()}",
        "[TgRedditBot](https://github.com/Kaif-00z/TgRedditBot)",
    )
    if not edit:
        return await event.reply(
            x,
            file="thumb.jpg",
            link_preview=False,
        )
    await event.edit(x, link_preview=False)


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("inf")))
async def infoo(event):
    await about(event, edit=True)


@bot.on(events.NewMessage(incoming=True, pattern="^/about$"))
async def _about(event):
    await about(event)


@bot.on(events.NewMessage(incoming=True, pattern="^/restart$"))
async def restart(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    try:
        if os.path.exists(".git"):
            await bash("git pull")
        if os.path.exists("requirements.txt"):
            await bash("pip3 install -U -r requirements.txt")
        await xx.edit("`Restarting...`")
        dB.set("RESTART", str([xx.chat_id, xx.id]))
        os.execl(sys.executable, sys.executable, "bot.py")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        dB.delete("RESTART")
        LOGS.error(format_exc())


async def on_start():
    try:
        xx = eval(dB.get("RESTART") or "[]")
        if xx:
            x = await bot.get_messages(xx[0], ids=xx[1])
            await x.edit("`Restarted`")
            dB.delete("RESTART")
        await bash(
            "wget https://telegra.ph/file/2a37745048a2d07323e05.jpg -O thumb.jpg"
        )
        xxx = eval(dB.get("WATCH_LIST") or "{}")
        if xxx:
            for username in xxx.keys():
                vlu = username.split("|")
                future = asyncio.ensure_future(watch(vlu[0], vlu[1]))
                if username not in FUTURE:
                    FUTURE.update({username: future})
            LOGS.info("Subreddit(s) Streaming Started...")
        """
        if dB.get("INBOX_STREAM"):
            _future = asyncio.ensure_future(inbox_stream())
            STREAM_INBOX.append(_future)
            LOGS.info("Inbox Streaming Started...")
        """
    except Exception:
        await bash(
            "wget https://telegra.ph/file/2a37745048a2d07323e05.jpg -O thumb.jpg"
        )
        LOGS.error(format_exc())


# =========== Main =======================================================


@bot.on(events.NewMessage(incoming=True, pattern="^/mycommunites$"))
async def mycomu(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    btn = [
        [Button.inline("Where I am Moderator", data="modcomu")],
        [Button.inline("Where I am Approved", data="apcomu")],
        [Button.inline("All Communities Where I am Present", data="comu")],
    ]
    await event.reply("Choose Option", buttons=btn)


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("comu")))
async def sim_comu(event):
    try:
        text = "<b>List Of Subscribed Subreddits</b>\n\n"
        async for community in reddit.user.subreddits():
            text += f"<code>•</code> <b><a href='https://www.reddit.com{community.url}'>{community.url.split('/')[-2]}</a></b>\n"
        await event.edit(text, link_preview=False, parse_mode="HTML")
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("modcomu")))
async def mod_comu(event):
    try:
        text = "<b>List Of Subreddits Where You Are Moderator</b>\n\n"
        async for community in reddit.user.moderator_subreddits():
            text += f"<code>•</code> <b><a href='https://www.reddit.com{community.url}'>{community.url.split('/')[-2]}</a></b>\n"
        await event.edit(text, link_preview=False, parse_mode="HTML")
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("apcomu")))
async def appr_comu(event):
    try:
        text = "<b>List Of Subreddits Where You Are Approved</b>\n\n"
        async for community in reddit.user.contributor_subreddits():
            text += f"<code>•</code> <b><a href='https://www.reddit.com{community.url}'>{community.url.split('/')[-2]}</a></b>\n"
        await event.edit(text, link_preview=False, parse_mode="HTML")
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/trusted$"))
async def trust_user(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    try:
        text = "<b>List Of Trusted User</b>\n\n"
        trusted_users = await reddit.user.trusted()
        for user in trusted_users:
            text += f"<code>•</code> <b><a href='https://www.reddit.com/u/{user.name}'>{user.name}</a></b>\n"
        await xx.edit(text, link_preview=False, parse_mode="HTML")
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/friends$"))
async def frnds(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    try:
        text = "<b>List Of Friends</b>\n\n"
        frnds = await reddit.user.friends()
        for user in frnds:
            text += f"<code>•</code> <b><a href='https://www.reddit.com/u/{user.name}'>{user.name}</a></b>\n"
        await xx.edit(text, link_preview=False, parse_mode="HTML")
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/blocked$"))
async def trust_user(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    try:
        text = "<b>List Of Blocked User</b>\n\n"
        ban = await reddit.user.blocked()
        for user in ban:
            text += f"<code>•</code> <b><a href='https://www.reddit.com/u/{user.name}'>{user.name}</a></b>\n"
        await xx.edit(text, link_preview=False, parse_mode="HTML")
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/pin ?(.*)"))
async def pinn(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    link = event.pattern_match.group(1)
    xx = await event.reply(PRO)
    try:
        mod_in = []
        async for community in reddit.user.moderator_subreddits():
            mod_in.append(community.url)
        if not link:
            me = await reddit.user.me()
            async for post in me.submissions.new():
                await post.subreddit.load()
                if post.subreddit.url in mod_in:
                    await post.mod.sticky()
                    await xx.edit(
                        "`Succesfully Pinned The Latest Submission`",
                        buttons=[[Button.url("Pinned Submission", url=post.url)]],
                    )
                else:
                    await xx.edit(
                        f"`Can't Pinned The Latest` [Submission]({post.url}) `Because Your Not Moderator in Following Subreddit`"
                    )
                return
        hmm = is_reddit_link(link)
        if not hmm:
            return await xx.edit("`Invalid Link`")
        submission = await reddit.submission(url=link, fetch=True)
        await submission.subreddit.load()
        if submission.subreddit.url not in mod_in:
            return await xx.edit(
                f"`Can't Pinned The Given` [Submission]({submission.url}) `Because Your Not Moderator in Following Subreddit`"
            )
        await submission.mod.sticky()
        await xx.edit(
            "`Succesfully Pinned The Given Submission`",
            buttons=[[Button.url("Pinned Submission", url=submission.url)]],
        )
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/unpin ?(.*)"))
async def umpinn(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    link = event.pattern_match.group(1)
    xx = await event.reply(PRO)
    try:
        mod_in = []
        async for community in reddit.user.moderator_subreddits():
            mod_in.append(community.url)
        if not link:
            me = await reddit.user.me()
            async for post in me.submissions.new():
                await post.subreddit.load()
                if post.subreddit.url in mod_in:
                    await post.mod.sticky(state=False)
                    await xx.edit(
                        "`Succesfully UnPinned The Latest Submission`",
                        buttons=[[Button.url("Pinned Submission", url=post.url)]],
                    )
                else:
                    await xx.edit(
                        f"`Can't UnPinned The Latest` [Submission]({post.url}) `Because Your Not Moderator in Following Subreddit`"
                    )
                return
        hmm = is_reddit_link(link)
        if not hmm:
            return await xx.edit("`Invalid Link`")
        submission = await reddit.submission(url=link, fetch=True)
        await submission.subreddit.load()
        if submission.subreddit.url not in mod_in:
            return await xx.edit(
                f"`Can't UnPinned The Given` [Submission]({submission.url}) `Because Your Not Moderator in Following Subreddit`"
            )
        await submission.mod.sticky(state=False)
        await xx.edit(
            "`Succesfully UnPinned The Given Submission`",
            buttons=[[Button.url("Pinned Submission", url=submission.url)]],
        )
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/feed ?(.*)"))
async def front_feed(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    try:
        no = event.pattern_match.group(1)
        if not no:
            no = 5
        number = int(no)
    except BaseException:
        return await xx.edit("`Wrong Input, Ex-` `/feed 10`")
    try:
        async for submission in reddit.front.hot(limit=number):
            await submission.subreddit.load()
            if submission.url.endswith((".gif", ".jpg", ".png")):
                await event.reply(
                    f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Full Text</code> - {submission.selftext}\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>"
                    if submission.selftext
                    else f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>",
                    file=await get_media(submission, LOGS),
                    buttons=[[Button.url("VIEW", url=f"https://redd.it/{submission}")]],
                    link_preview=False,
                    parse_mode="HTML",
                )
            else:
                try:
                    data = submission.secure_media["reddit_video"]
                except BaseException:
                    data = {}
                _file = await get_media(submission, LOGS)
                await event.reply(
                    f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Full Text</code> - {submission.selftext}\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>"
                    if submission.selftext
                    else f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>",
                    file=_file,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=data.get("duration", 0),
                            w=data.get("width", 512),
                            h=data.get("height", 512),
                            supports_streaming=True,
                        )
                    ],
                    thumb=await get_thumb(_file),
                    buttons=[[Button.url("VIEW", url=f"https://redd.it/{submission}")]],
                    link_preview=False,
                    parse_mode="HTML",
                )
            await asyncio.sleep(1)
        await xx.delete()
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


async def watch(username, id):
    try:
        subreddit = await reddit.subreddit(username)
        async for submission in subreddit.stream.submissions(skip_existing=True):
            await submission.subreddit.load()
            LOGS.info(
                f"New Submission from https://www.reddit.com{submission.subreddit.url}"
            )
            if submission.url.endswith((".gif", ".jpg", ".png")):
                await bot.send_message(
                    id,
                    f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Full Text</code> - {submission.selftext}\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>"
                    if submission.selftext
                    else f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>",
                    file=await get_media(submission, LOGS),
                    buttons=[[Button.url("VIEW", url=f"https://redd.it/{submission}")]],
                    link_preview=False,
                    parse_mode="HTML",
                )
            else:
                try:
                    data = submission.secure_media["reddit_video"]
                except BaseException:
                    data = {}
                _file = await get_media(submission, LOGS)
                await bot.send_message(
                    id,
                    f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Full Text</code> - {submission.selftext}\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>"
                    if submission.selftext
                    else f"<code>Title</code> - <b>{submission.title}</b>\n\n<code>Subreddit</code> - <b><a href='https://www.reddit.com{submission.subreddit.url}'>{submission.subreddit}</a></b>\n\n<code>Author</code> - <b><a href='https://www.reddit.com/u/{submission.author}/'>{submission.author}</a></b>",
                    file=_file,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=data.get("duration", 0),
                            w=data.get("width", 512),
                            h=data.get("height", 512),
                            supports_streaming=True,
                        )
                    ],
                    thumb=await get_thumb(_file),
                    buttons=[[Button.url("VIEW", url=f"https://redd.it/{submission}")]],
                    link_preview=False,
                    parse_mode="HTML",
                )
    except Exception as error:
        await bot.send_message(id, f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/watch ?(.*)"))
async def watcher(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    username = event.pattern_match.group(1)
    if not username:
        return await xx.edit("`UserName Not Found`")
    try:
        w_list = eval(dB.get("WATCH_LIST") or "{}")
        future = asyncio.ensure_future(watch(username, event.chat_id))
        if f"{username}|{event.chat_id}" not in FUTURE:
            FUTURE.update({f"{username}|{event.chat_id}": future})
            w_list.update({f"{username}|{event.chat_id}": event.chat_id})
            dB.set("WATCH_LIST", str(w_list))
            return await xx.edit(
                f"`Successfully Added This on This Chat's Watching List, To Unwatch this do` `/unwatch {username}`"
            )
        await xx.edit("`Already on Watching List`")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/unwatch ?(.*)"))
async def unwatcher(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    username = event.pattern_match.group(1)
    if not username:
        return await xx.edit("`Username Not Given`")
    try:
        _username = f"{username}|{event.chat_id}"
        if FUTURE.get(_username):
            w_list = eval(dB.get("WATCH_LIST") or "{}")
            FUTURE[_username].cancel()
            del FUTURE[_username]
            if w_list.get(_username):
                del w_list[_username]
                dB.set("WATCH_LIST", str(w_list))
            return await xx.edit(
                "`Succesfully Removed it from This Chat's Watching List`"
            )
        await xx.edit("`Username Not Found In This Chat's Watching List`")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/listwatch$"))
async def watch_list(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    await event.reply(
        "`Choose...`",
        buttons=[
            [
                Button.inline("All Chats", data="alchwlst"),
                Button.inline("This Chat Only", data="tschwlst"),
            ]
        ],
    ),


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("alchwlst")))
async def lst_watch(event):
    try:
        txt = "**Watch List Of All Chats**\n\n"
        for u in FUTURE.keys():
            vlu = u.split("|")
            txt += f"[{vlu[0]}](https://reddit.com/r/{vlu[0]}) - `[{vlu[1]}]`\n"
        await event.edit(txt, link_preview=False)
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("tschwlst")))
async def lst_ch_watch(event):
    try:
        txt = "**Watch List Of This Chat**\n\n"
        for u in FUTURE.keys():
            vlu = u.split("|")
            if str(event.chat_id) in vlu:
                txt += f"[{vlu[0]}](https://reddit.com/r/{vlu[0]})\n"
        await event.edit(txt, link_preview=False)
    except Exception as error:
        await event.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True))
async def incoreply(event):
    if not event.reply_to:
        return
    if str(event.sender_id) not in Var.OWNER:
        return
    reply = await event.get_reply_message()
    msg = event.text
    try:
        is_og = reply.sender_id
        og = (await event.client.get_me()).id
        if is_og != og:
            return
        url = await reply.click(0)
    except BaseException:
        return
    xx = await event.reply(PRO)
    try:
        if msg.startswith((".", "/")):
            return await xx.edit("`You Can't start the message with '.' and '/'`")
        submission = await reddit.submission(url=url)
        await submission.reply(msg)
        await xx.edit("`Successfully Replied`")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/join ?(.*)"))
async def join(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    username = event.pattern_match.group(1)
    if not username:
        return await xx.edit("`Username Not Given`")
    try:
        subreddit = await reddit.subreddit(username)
        await subreddit.load()
        await subreddit.subscribe()
        await xx.edit(
            f"<code>Succesfully Joined</code> <b><a href='https://www.reddit.com{subreddit.url}'>{subreddit}</a></b>",
            parse_mode="HTML",
        )
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/info ?(.*)"))
async def subinfo(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    username = event.pattern_match.group(1)
    if not username:
        return await xx.edit("`Username Not Given`")
    try:
        subreddit = await reddit.subreddit(username, fetch=True)
        if len(subreddit.description) > 100:
            desc = subreddit.description[:72] + "..."
        else:
            desc = subreddit.description
        msg = SUB_INFO.format(
            subreddit.display_name,
            subreddit.id,
            f"[{subreddit.display_name}](https://www.reddit.com{subreddit.url})",
            desc or None,
            subreddit.created_utc,
            subreddit.over18,
            subreddit.spoilers_enabled,
            subreddit.subscribers,
            subreddit.user_is_moderator,
            subreddit.user_is_subscriber,
            subreddit.user_is_banned,
        )
        await event.reply(msg, file=subreddit.icon_img or None, link_preview=False)
        await xx.delete()
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


""" Todo Stuffs"""

"""

@bot.on(events.NewMessage(incoming=True, pattern="^/inbox$"))
async def _inbox_opt(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    btn = [
        [
            Button.inline("Enable it", data="strmin"),
            Button.inline("Disable it", data="disstrmin"),
        ]
    ]
    await event.reply("`Stream Inbox:`", buttons=btn)


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("strmin")))
async def _stream_inbox(event):
    xx = await event.edit(PRO)
    if STREAM_INBOX:
        return await xx.edit("`Inbox Is Already Streaming... 😑😑`")
    try:
        future = asyncio.ensure_future(inbox_stream())
        STREAM_INBOX.append(future)
        dB.set("INBOX_STREAM", "True")
        await xx.edit("`Successfully Enabled Inbox Streaming...`")
        LOGS.info("Successfully Enabled Inbox Streaming...")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("disstrmin")))
async def _stop_stream_inbox(event):
    xx = await event.edit(PRO)
    if not STREAM_INBOX:
        return await xx.edit("`Inbox Streaming Already Disabled... 😑😑`")
    try:
        STREAM_INBOX[0].cancel()
        STREAM_INBOX.clear()
        dB.delete("INBOX_STREAM")
        await xx.edit("`Successfully Disabled Inbox Streaming...`")
        LOGS.info("Successfully Disabled Inbox Streaming...")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


async def inbox_stream():
    ids = [int(id) for id in Var.OWNER_ID.split()]
    try:
        async for pm in reddit.inbox.stream(skip_existing=True):
            for id in ids:
                await bot.send_message(
                    id,
                    INBOX.format(pm.subject, pm.body, pm.author, pm.was_comment),
                    buttons=[[Button.url("VIEW", url=f"https://redd.it/{pm.id}")]],
                )
    except Exception as error:
        for id in ids:
            await bot.send_message(id, f"`Error` - {error}")
        LOGS.error(format_exc())
"""


LOGS.info("Bot has Started...")
bot.loop.run_until_complete(on_start())
bot.loop.run_forever()
