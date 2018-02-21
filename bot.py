import datetime
import time

import discord
import configparser
import sys
import traceback
import pymysql.cursors
from discord.ext import commands
from pathlib import Path
from discord import abc

# Checking if the example config was copied
from utils import BugLog

config_file = Path('config.ini')
if config_file.exists() is not True:
    sys.exit("I'm sorry, but i can't find your config file. Make sure to copy"
             + "the Config.ini.example as config.ini and insert your settings")

# parsing our config
config = configparser.ConfigParser()
config.read('config.ini')


connection = pymysql.connect(host=config['Credentials']['host'],
                             user=config['Credentials']['user'],
                             password=config['Credentials']['password'],
                             db=config['Credentials']['database'],
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

with open('db-setup.sql', 'r') as inserts:
    for statement in inserts:
        connection.cursor().execute(statement)
        connection.commit()

# Preparing the cogs
initial_extensions = ['cogs.moderation',
                      'cogs.modlog',
                      'cogs.serverutils',
                      'cogs.fun',
                      'cogs.reminder',
                      'cogs.maintenance']

# Preparing the bot
bot = commands.Bot(command_prefix=config['Settings']['prefix'],
                   description='A Bot which watches Bug Hunters')

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if (isinstance(error, commands.CommandNotFound)):
        return
    if isinstance(error, commands.CheckFailure):
        # just a random user trying something he's not allowed to do
        await ctx.send(":lock: You do not have the required permissions to run this command")
    elif isinstance(error, discord.Forbidden):
        # permission misconfigurations
        BugLog.error(f"Encountered a permissions error while executing {ctx.command}")
        await ctx.send("Something does not seem to be configured right, i do not have all the permissions required by this command")
    elif isinstance(error, commands.TooManyArguments):
        await ctx.send("More arguments where supplied then i know how to handle")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("This command is dissabled")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command does not work in private messages")
    elif isinstance(error, commands.MissingRequiredArgument)\
            or isinstance(error, commands.BadArgument)\
            or isinstance(error, commands.MissingPermissions)\
            or isinstance(error, commands.BotMissingPermissions):
        await ctx.send(error)
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)

    else:
        # log to logger first just in case botlog logging fails as well
        BugLog.exception(f"Command execution failed:"
                                 f"    Command: {ctx.command}"
                                 f"    Message: {ctx.message.content}"
                                 f"    Channel: {'Private Message' if isinstance(ctx.channel, abc.PrivateChannel) else ctx.channel.name}"
                                 f"    Sender: {ctx.author.name}#{ctx.author.discriminator}"
                                 f"    Exception: {error}", error)
        #notify caller
        await ctx.send(":rotating_light: Something went wrong while executing that command :rotating_light:")

        embed = discord.Embed(colour=discord.Colour(0xff0000),
                              timestamp=datetime.datetime.utcfromtimestamp(time.time()))

        embed.set_author(name="Command execution failed:")
        embed.add_field(name="Command", value=ctx.command)
        embed.add_field(name="Original message", value=ctx.message.content)
        embed.add_field(name="Channel", value='Private Message' if isinstance(ctx.channel, abc.PrivateChannel) else ctx.channel.name)
        embed.add_field(name="Sender", value=f"{ctx.author.name}#{ctx.author.discriminator}")
        embed.add_field(name="Exception", value=error)
        v = ""
        for line in traceback.format_tb(error.__traceback__):
            v = f"{v}\n{line}"
        embed.add_field(name="Stacktrace", value=v)
        await BugLog.logToBotlog(embed=embed)


@bot.event
async def on_error(event, *args, **kwargs):
    #something went wrong and it might have been in on_command_error, make sure we log to the log file first
    BugLog.error(f"error in {event}\n{args}\n{kwargs}")
    BugLog.error(traceback.format_exc())
    embed = discord.Embed(colour=discord.Colour(0xff0000),
                          timestamp=datetime.datetime.utcfromtimestamp(time.time()))

    embed.set_author(name=f"Caught an error in {event}:")

    embed.add_field(name="args", value=str(args))
    embed.add_field(name="kwargs", value=str(kwargs))
    embed.add_field(name="Stacktrace", value=traceback.format_exc())
    await BugLog.logToBotlog(embed=embed)
    #try logging to botlog, wrapped in an try catch as there is no higher lvl catching to prevent taking donwn the bot (and if we ended here it might have even been due to trying to log to botlog
    try:
        pass
    except Exception as ex:
        BugLog.exception(f"Failed to log to botlog, eighter discord broke or something is seriously wrong!\n{ex}", ex)

# Adding the cogs to the bot
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            BugLog.startupError(f"Failed to load extention {extension}", e)


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}'
          + '\nVersion: {discord.__version__}\n')
    await BugLog.onReady(bot, config["Settings"]["botlog"])
    await bot.change_presence(game=discord.Game(name='BugHunters',
                                                type=3))

bot.run(config['Credentials']['Token'], bot=True)
