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


import asyncio
import re
import secrets
from urllib.parse import unquote

import aiohttp


def ts(milliseconds):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s") if seconds else "")
    )
    if not tmp:
        return "0s"

    if tmp.endswith(":"):
        return tmp[:-1]
    return tmp


def is_reddit_link(link):
    xx = re.match(r"https?://.+\.reddit\.\S+", link)
    return bool(xx)


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()


async def dl(url):
    link = url.replace("?source=fallback", "")
    async with aiohttp.ClientSession() as session:
        async with session.get(link, timeout=None) as response:
            filename = unquote(link.rpartition("/")[-1])
            with open(filename, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        f.write(chunk)
        return filename


async def get_media(submission, log):
    try:
        if submission.url.endswith((".jpg", ".png")):
            return await dl(submission.url)
        elif submission.url.endswith(".gif"):
            return submission.url
        elif submission.secure_media.get("reddit_video").get("fallback_url"):
            return await dl(submission.secure_media["reddit_video"]["fallback_url"])
        else:
            return None
    except Exception:
        return None


async def get_thumb(file):
    thumb_name = secrets.token_hex(nbytes=8) + ".jpg"
    await bash(f'ffmpeg -i """{file}""" -ss 1 -vframes 1 """{thumb_name}"""')
    return thumb_name
