import discord
from discord.ext import commands
from utils import permissions


class ModlogCog:
    """This cog includes all the features of the modlog"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return permissions.hasPermission(ctx.author.roles, "modlog", ctx.command)


def setup(bot):
    bot.add_cog(ModlogCog(bot))
