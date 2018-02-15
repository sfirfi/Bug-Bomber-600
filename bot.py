import discord
import configparser
import sys
import traceback
import pymysql.cursors
from discord.ext import commands
from pathlib import Path

# Checking if the example config was copied

config_file = Path('config.ini')
if config_file.exists() is not True:
    sys.exit("I'm sorry, but i can't find your config file. Make sure to copy"
             + "the Config.ini.example as config.ini and insert insert"
             + "your settings")

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

# Adding the cogs to the bot
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension', {extension}, file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}'
          + '\nVersion: {discord.__version__}\n')
    await bot.change_presence(game=discord.Game(name='BugHunters',
                                                type=3))

@bot.event
async def on_command_error(ctx:commands.Context, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("ACCESS DENIED")

bot.run(config['Credentials']['Token'], bot=True)
