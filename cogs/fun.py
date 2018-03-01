# This cog includes the fun comments so !hug, fight, cat etc

import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import random

from utils import permissions
from utils import Util

class FunCog:
    hugs = []
    fights = []
    async def __local_check(self, ctx: commands.Context):
        return await permissions.hasPermission(ctx, "fun")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5 * 60, BucketType.user)
    async def hug(self, ctx: commands.Context, friend: discord.Member):
        """Hugs a Person"""
        if friend == ctx.author:
            await ctx.send("You must be realy lonely if you need to hug yourself, have one from me instead!")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(FunCog.hugs[random.randint(0, len(FunCog.hugs)-1)].format(friend.mention, ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5 * 60, BucketType.user)
    async def fight(self, ctx: commands.Context, victim: discord.Member):
        """Fights a Person"""
        if victim == ctx.author:
            await ctx.send("How would you even do that?")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(FunCog.fights[random.randint(0, len(FunCog.fights)-1)].format(victim.mention, ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2.5 * 60, BucketType.user)
    async def pet(self, ctx: commands.Context, friend: discord.Member):
        """Pets a person"""
        if friend == ctx.author:
            await ctx.send("Petting yourself, how would you even do that?")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send("{0}: {1} pets you".format(friend.mention, ctx.author.mention))

    def __init__(self, bot):
        self.bot = bot
        funny = Util.fetchFromDisk("fun-info")
        FunCog.hugs = funny["hugs"]
        FunCog.fights = funny["fights"]




def setup(bot):
    bot.add_cog(FunCog(bot))
