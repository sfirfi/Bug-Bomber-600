import pymysql.cursors
import configparser


# creates a connection to the DB
from discord.ext import commands


def get_connection():
    config = configparser.ConfigParser()
    config.read('config.ini')
    connection = pymysql.connect(host=config['Credentials']['host'],
                                 user=config['Credentials']['user'],
                                 password=config['Credentials']['password'],
                                 db=config['Credentials']['database'],
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


# Receives a permissions and the roles of a user
# Checks if any of the roles has the needed Permission
def hasPermission(roles, cog, command):
    conn = get_connection()
    for crole in roles:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, permission FROM permissions where role_id='{crole.id}' AND (permission = '*' OR permission = '{cog}.*' OR permission = '{cog}.{command}');")
        if len(cursor.fetchall()) is not 0:
            return True

    return False


def owner_only():
    async def predicate(ctx):
        return ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)
