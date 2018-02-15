import discord
from discord.ext import commands
from utils import permissions


class ServerutilsCog:
    """This cog includes the server utils so self assignable roles and the server"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return permissions.hasPermission(ctx.author.roles, "utils", ctx.command)


def setup(bot):
    bot.add_cog(ServerutilsCog(bot))
