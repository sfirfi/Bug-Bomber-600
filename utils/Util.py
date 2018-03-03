import json
import aiohttp
import asyncio
import async_timeout
import datetime

from discord.ext import commands


def fetchFromDisk(filename):
    try:
        with open(f"{filename}.json") as file:
            return json.load(file)
    except FileNotFoundError:
        return dict()


def saveToDisk(filename, dict):
    with open(f"{filename}.json") as file:
        json.dump(dict, file, indent=4, skipkeys=True, sort_keys=True)


def convertToSeconds(value: int, type: str):
    type = type.lower()
    if len(type) > 1 and type[-1:] == 's': # plural -> singular
        type = type[:-1]
    if type == 'w' or type == 'week':
        value = value * 7
        type = 'd'
    if type == 'd' or type == 'day':
        value = value * 24
        type = 'h'
    if type == 'h' or type == 'hour':
        value = value * 60
        type = 'm'
    if type == 'm' or type == 'minute':
        value = value * 60
        type = 's'
    if type != 's' and type != 'second':
        raise commands.BadArgument(f"Invalid duration: `{type}`\nValid identifiers: week(s), day(s), hour(s), minute(s), second(s)")
    else:
        return value

async def fetchFromWeb(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def grepJsonFromWeb(url):
    async with aiohttp.ClientSession() as session:
        content = await fetchFromWeb(session, url)
        return json.loads(content)

async def grepFromWeb(url):
     async with aiohttp.ClientSession() as session:
        content = await fetchFromWeb(session, url)
        return content


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)

