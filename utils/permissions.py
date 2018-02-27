import pymysql.cursors
import configparser


# creates a connection to the DB
from discord.ext import commands

# Receives a permissions and the roles of a user
# Checks if any of the roles has the needed Permission


def hasPermission(roles, cog, command):
    conn = cog.bot.DBC
    for crole in roles:
        conn.query(f"SELECT id, permission FROM permissions where role_id='{crole.id}' AND (permission = '*' OR permission = '{cog}.*' OR permission = '{cog}.{command}');")
        if len(conn.fetch_rows()) is not 0:
            return True

    return False


def owner_only():
    async def predicate(ctx):
        return ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)
