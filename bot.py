#!/usr/bin/env python3
import asyncio
import datetime
import time

import discord
import configparser
import sys
import os
import traceback
import pymysql.cursors
from discord.ext import commands
from pathlib import Path
from discord import abc
from peewee import MySQLDatabase
from cryptography.fernet import Fernet
from utils import Configuration, DatabaseConnector, Util, cryption

# Checking if the example config was copied
from cogs.fun import FunCog
from utils import BugLog, Database

if not os.path.exists('config'):
    os.makedirs('config')

config_file = Path('config.ini')
if config_file.exists() is not True:
    sys.exit("I'm sorry, but i can't find your config file. Make sure to copy"
             + "the Config.ini.example as config.ini and insert your settings")

# parsing our config
config = configparser.ConfigParser()
config.read('config.ini')


connection = Database.SQLDB(host=config['Credentials']['host'],
                             user=config['Credentials']['user'],
                             password=config['Credentials']['password'],
                             database=config['Credentials']['database'])
try:
    print("Loading AES-Key")
    keyFile = open('encryption_key.txt', 'r')
except:
    print("No stored AES-Key was found. Generatinga new Key.")
    newKeyFile = open('encryption_key.txt', 'w')
    newKeyFile.write("This file is used to store the encryption key for end user Data in the DB. Do not edit or remove this file as this would make your stored data forever useless.\n")
    newKeyFile.write("----- Start of the AES-Key -----\n")
    newKeyFile.write(Fernet.generate_key().decode() + "\n")
    newKeyFile.write("-----  End of the AES-key  -----")
    newKeyFile.close()
    keyFile = open('encryption_key.txt', 'r')


key = str.encode(keyFile.readlines()[2])
keyFile.close()

#TODO: wrap in try catch
with open('db-setup.sql', 'r') as inserts:
    for statement in inserts:
        connection.query(statement)
        pass


# Preparing the cogs
initial_extensions = ['moderation',
                      'modlog',
                      'utils',
                      'fun',
                      'reminder',
                      'maintenance',
                      'serveradmin']

def prefix_callable(bot, msg):
    user_id = bot.user.id
    prefixes =  [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None or not bot.startup_done:
        prefixes.append('!') #use default ! prefix in DMs
    else:
        prefixes.append(Configuration.getConfigVar(msg.guild.id, "PREFIX"))
    return prefixes

# Preparing the bot
bot = commands.Bot(command_prefix=prefix_callable,
                   description='A bot who watches Bug Hunters')

bot.DBC = connection
bot.config = config
bot.starttime = datetime.datetime.now()
bot.startup_done = False
bot.aes = cryption.FernetEncryption(key)


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages.")
    elif isinstance(error, commands.BotMissingPermissions):
        BugLog.error(f"Encountered a permissions error while executing {ctx.command}.")
        ctx.command.reset_cooldown(ctx)
        await ctx.send(error)
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("Sorry. This command is disabled and cannot be used.")
    elif isinstance(error, commands.CheckFailure):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            await ctx.send(":lock: You do not have the required permissions to run this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"You are missing a required argument! (See !help {ctx.command.qualified_name} for info on how to use this command).")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument given! (See !help {ctx.command.qualified_name} for info on how to use this commmand).")
        ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send(":rotating_light: Something went wrong while executing that command. :rotating_light:")
        # log to logger first just in case botlog logging fails as well
        BugLog.exception(f"Command execution failed:"
                                f"    Command: {ctx.command}"
                                f"    Message: {ctx.message.content}"
                                f"    Channel: {'Private Message' if isinstance(ctx.channel, abc.PrivateChannel) else ctx.channel.name}"
                                f"    Sender: {ctx.author.name}#{ctx.author.discriminator}"
                                f"    Exception: {error}", error)

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
            if len(v) + len(line) > 1024:
                embed.add_field(name="Stacktrace", value=v)
                v = ""
            v = f"{v}\n{line}"
        if len(v) > 0:
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
    #try logging to botlog, wrapped in an try catch as there is no higher lvl catching to prevent taking donwn the bot (and if we ended here it might have even been due to trying to log to botlog
    try:
        await BugLog.logToBotlog(embed=embed)
    except Exception as ex:
        BugLog.exception(f"Failed to log to botlog, either Discord broke or something is seriously wrong!\n{ex}", ex)



# Adding the cogs to the bot
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
        except Exception as e:
            BugLog.startupError(f"Failed to load extention {extension}.", e)


@bot.event
async def on_guild_join(guild: discord.Guild):
    BugLog.info(f"A new guild came up: {guild.name} ({guild.id}).")
    Configuration.loadConfig(guild)



@bot.event
async def on_ready():
    if not bot.startup_done:
        await Configuration.onReady(bot)
        print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}' + f'\nVersion: {discord.__version__}\n')
        await BugLog.onReady(bot, config["Settings"]["botlog"])
        bot.loop.create_task(keepDBalive())  # ping DB every hour so it doesn't run off
        await bot.change_presence(activity=discord.Activity(name='BugHunters', type=discord.ActivityType.watching))
        bot.startup_done = True

@bot.event
async def on_message(message:discord.Message):
    if message.author.bot:
        return
    ctx:commands.Context = await bot.get_context(message)
    if ctx.command is not None:
        if isinstance(ctx.channel, discord.TextChannel) and not ctx.channel.permissions_for(ctx.channel.guild.me).send_messages:
            try:
                await ctx.author.send("Hey, you tried triggering a command in a channel I'm not allowed to send messages in. Please grant me permissions to reply and try again.")
            except Exception:
                pass #closed DMs
        else:
            await bot.invoke(ctx)

async def keepDBalive():
    while not bot.is_closed():
        bot.database_connection.connection().ping(True)
        await asyncio.sleep(3600)
DatabaseConnector.init()
bot.database_connection: MySQLDatabase = DatabaseConnector.connection
bot.run(config['Credentials']['Token'], bot=True)

time.sleep(5)
