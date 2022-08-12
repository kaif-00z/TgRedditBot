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
from traceback import format_exc

from asyncpraw import Reddit
from redis import Redis
from telethon import Button, TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo
from telethon.utils import get_display_name

from helper import *
from strings import *
from var import Var

file = "tgreddit_bot.log"
if os.path.exists(file):
    os.remove(file)

basicConfig(
    format="%(asctime)s || %(name)s [%(levelname)s] : %(message)s",
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
    LOGS.critical(str(e))
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
    LOGS.critical(str(exc))
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
    LOGS.critical(str(eo))
    exit()

UPTIME = dt.now()
FUTURE = {}

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
        file="tgreddit_bot.log",
        force_document=True,
        thumb="thumb.jpg",
    )
    await xx.delete()


async def about(event, edit=False):
    from platform import python_version, release, system

    from asyncpraw.const import __version__ as praw_version
    from telethon import __version__ as telethon_version

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
        """
        await bash("git pull")
        if os.path.exists("requirements.txt"):
            await bash("pip3 install -U -r requirements.txt")
        """
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
        for username in xxx.keys():
            future = asyncio.ensure_future(watch(username, xxx[username]))
            if username not in FUTURE:
                FUTURE.update({username: future})
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
        future = asyncio.ensure_future(watch(username, event.sender_id))
        if username not in FUTURE:
            FUTURE.update({username: future})
            w_list.update({username: event.sender_id})
            dB.set("WATCH_LIST", str(w_list))
            return await xx.edit(
                f"`Successfully Added This on Watching List, To Unwatch this do` `/unwatch {username}`"
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
        if FUTURE.get(username):
            w_list = eval(dB.get("WATCH_LIST") or "{}")
            FUTURE[username].cancel()
            del FUTURE[username]
            if w_list.get(username):
                del w_list[username]
                dB.set("WATCH_LIST", str(w_list))
            return await xx.edit("`Succesfully Removed it from Watching List`")
        await xx.edit("`Username Not Found In Watching List`")
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True, pattern="^/listwatch$"))
async def watch_list(event):
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
    xx = await event.reply(PRO)
    try:
        txt = "**Watch List**\n\n"
        for u in FUTURE.keys():
            txt += f"[{u}](https://reddit.com/r/{u})\n"
        await xx.edit(txt)
    except Exception as error:
        await xx.edit(f"`Error` - {error}")
        LOGS.error(format_exc())


@bot.on(events.NewMessage(incoming=True))
async def incoreply(event):
    if not event.reply_to:
        return
    if str(event.sender_id) not in Var.OWNER:
        return await event.reply(AD)
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
            return await xx.edit("`You Can't start the message with'.' and '/'`")
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


LOGS.info("Bot has Started...")
bot.loop.run_until_complete(on_start())
bot.loop.run_forever()
