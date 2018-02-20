import logging
import sys
import traceback

import discord
from discord.ext import commands


logger = logging.getLogger('Bug-Bomber')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='Bug-Bomber.log', encoding='utf-8', mode='w+')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

BOT_LOG_CHANNEL:discord.TextChannel


def info(message):
    logger.info(message)


def warn(message):
    logger.warning(message)


def error(message):
    logger.error(message)

def exception(message, error):
    logger.error(message)
    traceback.format_tb(error.__traceback__)


async def onReady(client:commands.Bot, channelID):
    global BOT_LOG_CHANNEL
    BOT_LOG_CHANNEL = client.get_channel(int(channelID))
    if BOT_LOG_CHANNEL is None:
        logger.error("Logging channel is misconfigured, aborting startup!")
        await client.logout()
    info = await client.application_info()
    await logToBotlog(message=f"{info.name} ready get to work!")


async def logToBotlog(message = None, embed = None, log = True):
    await BOT_LOG_CHANNEL.send(content=message, embed=embed)
    if log:
        info(message)