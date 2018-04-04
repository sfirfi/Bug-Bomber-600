import discord
from discord.ext import commands
from utils import permissions


class ModlogCog:
    """This cog includes all the features of the modlog"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "fun")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

def setup(bot):
    bot.add_cog(ModlogCog(bot))
