# This cog includes the fun comments so !hug, fight, cat etc

import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import random

from utils import permissions
from utils import Util


class FunCog:
    async def __local_check(self, ctx: commands.Context):
        return permissions.hasPermission(ctx.author.roles, "fun", ctx.command)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 20 * 60, BucketType.user)
    async def hug(self, ctx: commands.Context, friend: discord.Member):
        if friend == ctx.author:
            await ctx.send("You must be realy lonely if you need to hug yourself, have one from me instead!")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(self.hugs[random.randint(0, len(self.hugs))].format(friend.mention, ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 20 * 60, BucketType.user)
    async def fight(self, ctx: commands.Context, friend: discord.Member):
        if friend == ctx.author:
            await ctx.send("How would you even do that?")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(self.fights[random.randint(0, len(self.fights))].format(friend.mention, ctx.author.mention))

    def __init__(self, bot):
        self.bot = bot
        funny = Util.fetchFromDisk("fun-info")
        self.hugs = funny["hugs"]
        self.fights = funny["fights"]




def setup(bot):
    bot.add_cog(FunCog(bot))
