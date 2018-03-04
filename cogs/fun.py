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

import configparser

class FunCog:
    config = configparser.ConfigParser()
    config.read('config.ini')
    hugs = []
    fights = []
    async def __local_check(self, ctx: commands.Context):
        return await permissions.hasPermission(ctx, "fun")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['hug'], BucketType.user)
    async def hug(self, ctx: commands.Context, friend: discord.Member):
        """Hugs a Person"""
        if friend == ctx.author:
            await ctx.send("You must be realy lonely if you need to hug yourself, have one from me instead!")
            ctx.command.reset_cooldown(ctx)
        elif friend == self.bot.user:
            await ctx.send("Thanks for the hug!")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(FunCog.hugs[random.randint(0, len(FunCog.hugs)-1)].format(friend.mention, ctx.author.name))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['fight'], BucketType.user)
    async def fight(self, ctx: commands.Context, victim: discord.Member):
        """Fights a Person"""
        if victim == ctx.author:
            await ctx.send("How would you even do that?")
            ctx.command.reset_cooldown(ctx)
        elif victim == self.bot.user:
            await ctx.send("You sure you want to do that? <:GhoulBan:417535190051586058>")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(FunCog.fights[random.randint(0, len(FunCog.fights)-1)].format(victim.mention, ctx.author.name))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['pet'], BucketType.user)
    async def pet(self, ctx: commands.Context, pet: discord.Member):
        """Pets a person"""
        if pet == ctx.author:
            await ctx.send("Petting yourself, how would you even do that?")
            ctx.command.reset_cooldown(ctx)
        elif pet == self.bot.user:
            await ctx.send("<a:typing:393881558169288716>")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send("{0}: {1} pets you".format(pet.mention, ctx.author.name))

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

    @commands.command()
    @commands.cooldown(1,config['Cooldowns']['cat'] , BucketType.user)
    async def cat(self, ctx: commands.Context):
        """Sends a cat image"""
        html = await Util.grepFromWeb('https://thecatapi.com/api/images/get?format=html')
        html = html.split('src="')
        img = html[1].replace('"></a>', '').replace('http', 'https')
        embed = discord.Embed(color=0x3dede6)
        embed.set_image(url=img)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['dog'], BucketType.user)
    async def dog(self, ctx: commands.Context):
        """Sends a dog image"""
        img = await Util.grepJsonFromWeb('http://random.dog/woof.json')
        embed = discord.Embed(color=0x136955)
        if img['url'].endswith(('mp4', 'webm')):
           await ctx.send(img['url'])
        else:
            embed.set_image(url=img['url'])
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['fox'], BucketType.user)
    async def fox(self, ctx: commands.Context):
        """Sends a fox image"""
        html = await Util.grepFromWeb('http://www.thedailyfox.org/random')
        html = html.split('<img src="')
        html = html[1].split('" alt="')
        img = html[0]
        embed = discord.Embed(color=0xa52a2a)
        embed.set_image(url=img)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['lizard'], BucketType.user)
    async def lizard(self, ctx: commands.Context):
        """Sends a lizard image"""
        img = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/lizard')
        embed = discord.Embed(color=0x198c19)
        embed.set_image(url=img['url'])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['neko'], BucketType.user)
    async def neko(self, ctx: commands.Context):
        """Sends a catgirl image"""
        img = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/neko')
        embed = discord.Embed(color=0xffffff)
        embed.set_image(url=img['url'])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['ahug'], BucketType.user)
    async def ahug(self, ctx: commands.Context):
        """Sends an anime hug image"""
        img = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/hug')
        embed = discord.Embed(color=0xe59400)
        embed.set_image(url=img['url'])
        await ctx.send(embed=embed)


    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['pat'], BucketType.user)
    async def pat(self, ctx: commands.Context):
        """Sends an anime pat image"""
        img = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/pat')
        embed = discord.Embed(color=0x730073)
        embed.set_image(url=img['url'])
        await ctx.send(embed=embed)

    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if self.bot.user in message.mentions and (":point_left:" in message.content or ":point_right:" in message.content or 'poke' in message.content):
            muted = commands.RoleConverter().convert("<@&391366395377483776>")
            await message.author.add_roles(muted)
            await message.channel.send(f"{message.author.mention} I do **NOT** appreciate being poked")
            await asyncio.sleep(2)
            await message.channel.send(f"Please don't do that again!")
            await asyncio.sleep(13)
            await message.author.remove_roles(muted)
            await asyncio.sleep(5*60)
            await message.channel.send(f"__pokes :point_left:{message.author.mention}:point_right:__")


    def __init__(self, bot):
        self.bot:commands.Bot = bot
        conn: SQLDB = self.bot.DBC
        config = bot.config
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
        FunCog.fights = []
        for fight in fights:
            FunCog.fights.append(fight["fight"])
        if len(FunCog.fights) == 0:
            fights = Util.fetchFromDisk("fun-info")["fights"]
            for fight in fights:
                FunCog.fights.append(fight)
                conn.query('INSERT INTO fights (fight, author) VALUES ("%s", "%d")' % (fight, 114407765400748041))




def setup(bot):
    bot.add_cog(FunCog(bot))
