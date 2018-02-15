# This cog includes the fun comments so !hug, fight, cat etc

import discord
from discord.ext import commands
from utils import permissions


class FunCog:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context):
        return permissions.hasPermission(ctx.author.roles, "moderation", ctx.command)


def setup(bot):
    bot.add_cog(FunCog(bot))
