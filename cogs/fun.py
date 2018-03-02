# This cog includes the fun comments so !hug, fight, cat etc
import asyncio

import discord
import time
from discord.ext import commands
from discord.ext.commands import BucketType, BadArgument
import random

from utils import permissions, BugLog
from utils.Database import SQLDB
from utils import Util

class FunCog:
    hugs = []
    fights = []
    async def __local_check(self, ctx: commands.Context):
        return await permissions.hasPermission(ctx, "fun")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1.5 * 60, BucketType.user)
    async def hug(self, ctx: commands.Context, friend: discord.Member):
        """Hugs a Person"""
        if friend == ctx.author:
            await ctx.send("You must be realy lonely if you need to hug yourself, have one from me instead!")
            ctx.command.reset_cooldown(ctx)
        elif friend == self.bot.user:
            await ctx.send("Thanks for the hug!")
        else:
            await ctx.send(FunCog.hugs[random.randint(0, len(FunCog.hugs)-1)].format(friend.mention, ctx.author.name))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1.5 * 60, BucketType.user)
    async def fight(self, ctx: commands.Context, victim: discord.Member):
        """Fights a Person"""
        if victim == ctx.author:
            await ctx.send("How would you even do that?")
            ctx.command.reset_cooldown(ctx)
        elif victim == self.bot.user:
            await ctx.send("You sure you want to do that? <:GhoulBan:417535190051586058>")
        else:
            await ctx.send(FunCog.fights[random.randint(0, len(FunCog.fights)-1)].format(victim.mention, ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 1 * 60, BucketType.user)
    async def pet(self, ctx: commands.Context, friend: discord.Member):
        """Pets a person"""
        if friend == ctx.author:
            await ctx.send("Petting yourself, how would you even do that?")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send("{0}: {1} pets you".format(friend.mention, ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    async def summon(self, ctx, *, target: str):
        """Summons a person"""
        try:
            member = await commands.MemberConverter().convert(ctx, target)
        except BadArgument as ex:
            await ctx.send(f"**I have summoned the one known as {target}!**")
            await asyncio.sleep(5)
            await ctx.send("Be prepared as there is no stopping this summoning!")
            await asyncio.sleep(5)
            await ctx.send("The summoning will be complete soon!")
            await asyncio.sleep(5)
            await ctx.send("_Please note that 'soon' in bot time is not always considered the same as 'soon' in human time_")
            await asyncio.sleep(5)
            await ctx.send("Have a nice day!")
        else:
            if target == ctx.author:
                await ctx.send("Summoning yourself? That's cheating!")
                ctx.command.reset_cooldown(ctx)
            else:
                await ctx.send(f"{member.name} is already a member of this server, do the ping youself, lazy humans")

    def __init__(self, bot):
        self.bot = bot
        conn: SQLDB = self.bot.DBC
        #loading hugs
        conn.query("SELECT * FROM hugs")
        hugs = conn.fetch_rows()
        FunCog.hugs = []
        for hug in hugs:
            FunCog.hugs.append(hug["hug"])
        if len(FunCog.hugs) == 0:
            hugs = Util.fetchFromDisk("fun-info")["hugs"]
            for hug in hugs:
                FunCog.hugs.append(hug)
                conn.query('INSERT INTO hugs (hug, author) VALUES ("%s", "%d")' % (hug, 114407765400748041))


        #loading fights
        conn.query("SELECT * FROM fights")
        fights = conn.fetch_rows()
        FunCog.hugs = []
        for fight in fights:
            FunCog.fights.append(fight["fight"])
        if len(FunCog.fights) == 0:
            fights = Util.fetchFromDisk("fun-info")["fights"]
            for fight in fights:
                FunCog.fights.append(fight)
                conn.query('INSERT INTO fights (fight, author) VALUES ("%s", "%d")' % (fight, 114407765400748041))




def setup(bot):
    bot.add_cog(FunCog(bot))
