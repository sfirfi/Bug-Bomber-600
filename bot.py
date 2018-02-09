import discord
import configparser
import sys
from discord.ext import commands
from pathlib import Path

# Checking if the example config was copied

config_file = Path('config.ini')
if config_file.exists() is not True:
    sys.exit("I'm sorry, but i can't find your config file. Make sure to copy the" \
           + "Config.ini.example as config.ini and insert insert your settings")

# pasring our config
config = configparser.ConfigParser()
config.read('config.ini')

bot = commands.Bot(command_prefix=config['Settings']['prefix'], description='A Bot which watches Bug Hunters')

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(game=discord.Game(name='Watching BugHunters'))

bot.run(config['Credentials']['Token'], bot=True)
